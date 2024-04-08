import logging
import re
from pathlib import Path

from telethon import events, Button

from core import database
from core import settings
from core.telegram.login import get_bot
from core.telegram.types import Message, CallbackQuery
from instagram.main import process_user, run_instagram
from instagram.utils import get_client
from telegram.notifications import send_telegram_notifications

# =================  CONFIG  ================= #

current_dir = Path(__file__).parent

bot = get_bot()
logging.basicConfig(
    filename="logs/bot.log",
    filemode="a",
    format="[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d - %H:%M:%S",
    level=logging.WARNING,
)

print(f"[✓] Telegram Bot [ @{settings.TELEGRAM_BOT_USERNAME} ] Started.")
logging.info(f"Telegram Bot [ @{settings.TELEGRAM_BOT_USERNAME} ] Started.")


@bot.on(events.NewMessage())
async def ignore_non_sudo_messages(message: Message):
    if message.sender_id not in settings.TELEGRAM_SUDO_IDS:
        raise events.StopPropagation


@bot.on(events.CallbackQuery())
async def ignore_non_private_callbacks(callback: CallbackQuery):
    if callback.sender_id not in settings.TELEGRAM_SUDO_IDS:
        raise events.StopPropagation


@bot.on(events.NewMessage(pattern=r"^/inspectors$"))
async def list_inspectors(message: Message):
    """
    /inspectors
    """

    inspectors = database.get.get_all_inspectors()
    if not inspectors:
        await message.respond(
            "**No active inspector available. Add one with** /add_inspector"
        )
        raise events.StopPropagation

    inspectors_list = "**Active Inspectors:**\n\n"
    for inspector in inspectors:
        inspectors_list += (
            f"**Username:** `{inspector.username}`\n"
            f"**IG ID:** `{inspector.ig_pk}`\n"
            f"/ins_{inspector.id}\n\n"
        )

    await message.respond(inspectors_list)
    raise events.StopPropagation


@bot.on(events.NewMessage(pattern=r"^/inspected_users"))
async def inspected_users_text(message: Message):
    """
    /inspected_users
    """

    inspected_users = database.get.get_all_inspected_users()
    if not inspected_users:
        await message.respond(
            "**No active under inspect user available. Add one with** /inspect"
        )
        raise events.StopPropagation

    text = "**Active Inspectors:**\n\n"
    for inspected_user in inspected_users:
        user_inspector = database.get.get_inspector(db_id=inspected_user.inspector)

        if not user_inspector:
            inspected_user.inspector = None
            database.update.update_inspected_user(inspected_user)

        text += (
            f"**Username:** [{inspected_user.username}](https://instagram.com/{inspected_user.username})\n"
            f"**ID:** `{inspected_user.ig_pk}`\n"
            f"**Followers:** `{inspected_user.follower_count}`\n"
            f"**Followings:** `{inspected_user.following_count}`\n"
            f"**Inspector:** `{user_inspector.username if user_inspector else '-'}`\n"
            f"/reassign_{inspected_user.id}  /delu_{inspected_user.id}\n\n"
        )

    await message.respond(text)
    raise events.StopPropagation


@bot.on(events.NewMessage(pattern=r"^/reassign_(\d+)$"))
async def reassign_inspected_user(message: Message):
    """
    /reassign_NUM. like /reassign_2
    """

    inspected_user_id = message.pattern_match.group(1)
    inspected_user = database.get.get_inspected_user(db_id=inspected_user_id)
    if not inspected_user:
        raise events.StopPropagation

    inspectors = database.get.get_all_inspectors()
    if not inspectors:
        await message.respond("No active inspector available.")
        raise events.StopPropagation

    text = "**Select the inspector you want assign to this user:**"
    buttons = [
        [
            Button.inline(
                inspector.username, f"reassign:{inspector.id}:{inspected_user.id}"
            )
        ]
        for inspector in inspectors
    ]

    await message.respond(text, buttons=buttons)
    raise events.StopPropagation


@bot.on(events.NewMessage(pattern=r"^/delu_(\d+)$"))
async def delete_inspected_user(message: Message):
    """
    /delu_NUM. like /delu_2
    """

    inspected_user_id = message.pattern_match.group(1)
    inspected_user = database.get.get_inspected_user(db_id=inspected_user_id)
    if not inspected_user:
        raise events.StopPropagation

    await message.respond(
        f"**Are you sure you want to delete** `{inspected_user.username}` **?**",
        buttons=[
            [
                Button.inline("Delete", f"delu:{inspected_user.id}:1"),
                Button.inline("Cancel", f"delu:{inspected_user.id}:0"),
            ]
        ],
    )
    raise events.StopPropagation


@bot.on(events.NewMessage(pattern=r"^/ins_(\d+)$"))
async def inspector_stats(message: Message):
    """
    /ins_NUM. like /ins_2
    """

    inspector_id = message.pattern_match.group(1)
    inspector = database.get.get_inspector(db_id=inspector_id)
    if not inspector:
        raise events.StopPropagation

    inspector_users = database.get.get_inspector_inspected_users(inspector)

    if not inspector_users:
        await message.respond(
            "**This inspector does not inspect anyone at the moment.**"
        )
        raise events.StopPropagation

    text = f"**Users being inspected by** `{inspector.username}`**:**\n\n"
    for user in inspector_users:
        text += (
            f"**Username:** [{user.username}](https://instagram.com/{user.username})\n"
            f"**ID:** `{user.ig_pk}`\n"
            f"**Followers:** `{user.follower_count}`\n"
            f"**Followings:** `{user.following_count}`\n"
            f"/reassign_{user.id}\n\n"
        )

    await message.reply(text, link_preview=False)
    raise events.StopPropagation


@bot.on(events.NewMessage(pattern=r"^(?:/add_inspector|/relogin)"))
async def add_inspector(message: Message):
    """
    /add_inspector USERNAME PASSWORD [2FA_CODE]
    """

    data = message.text.split()
    is_re_login = data[0] == "/relogin"

    try:
        username = data[1]
        password = data[2]
    except IndexError:
        await message.respond(
            f"**Usage:**\n "
            f"{'/relogin' if is_re_login else '/add_inspector'} USERNAME PASSWORD [2FA_CODE]`"
        )
        raise events.StopPropagation

    try:
        verification_code = data[3]
    except IndexError:
        verification_code = ""

    if is_re_login:
        inspector_object = database.get.get_inspector(username)
        if not inspector_object:
            await message.edit(
                f"**Inspector** `{username}` **does not exists.**",
                buttons=Button.clear(),
            )
            raise events.StopPropagation
        inspector_object.username = username
        inspector_object.password = password
        database.update.update_inspector(inspector_object)

    else:
        try:
            inspector_object = database.create.create_inspector(username, password)
        except ValueError as e:
            await message.reply(e.args[0])
            raise events.StopPropagation

    wait_message = await message.respond(
        message=(
            "**Logining-in to instagram using:**\n"
            f"**Username:** `{username}`\n"
            f"**Password:** `{password}`\n"
            f"**2FACode:** {verification_code or '-'}\n\n"
            f"..."
        ),
    )

    try:
        get_client(
            username,
            inspector_object.id,
            verification_code=verification_code,
            reloing=is_re_login,
        )
    except Exception as e:
        logging.error(f"Error loging-in to {username}: {e}", exc_info=True)
        await wait_message.reply(f"Error loging-in to {username}:\n `{e}`")
        database.delete.delete_inspector(inspector_object)
        raise events.StopPropagation

    await wait_message.reply("✅ Success")


@bot.on(events.NewMessage(pattern=r"^/del_inspector"))
async def delete_inspector_text(message: Message):
    """
    /del_inspector
    """

    inspectors = database.get.get_all_inspectors()
    if not inspectors:
        await message.respond("No active inspector available.")
        raise events.StopPropagation

    text = "**Select inspector to delete:**"
    buttons = [
        [Button.inline(inspector.username, f"del:{inspector.username}")]
        for inspector in inspectors
    ]

    await message.respond(text, buttons=buttons)
    raise events.StopPropagation


@bot.on(events.NewMessage(pattern=r"^/inspect"))
async def inspect_text(message: Message):
    """
    /inspect USERNAME
    """

    try:
        user_username = message.text.split()[1]
    except IndexError:
        await message.respond("**Usage:**\n`/inspect USERNAME`")
        raise events.StopPropagation

    if not re.match(r"^\w[\w.]+$", user_username):
        await message.respond("**Username is not valid**")
        raise events.StopPropagation

    user_already_exists = database.get.get_inspected_user(user_username)
    if user_already_exists:
        await message.respond("**This user is already under inspect.**")
        raise events.StopPropagation

    inspectors = database.get.get_all_inspectors()
    if not inspectors:
        await message.respond(
            "No active inspector available. "
            "To inspect users you need to first add an inspector using /add_inspector."
        )
        raise events.StopPropagation

    text = "**Which inspector should inspect this user?**"
    buttons = [
        [Button.inline(inspector.username, f"ins:{inspector.username}:{user_username}")]
        for inspector in inspectors
    ]
    await message.respond(text, buttons=buttons)
    raise events.StopPropagation


@bot.on(events.NewMessage(pattern="^/prune$$"))
async def prune_database_text(message: Message):
    """
    /prune
    """

    await message.respond(
        "**Pruning the database will delete all orphan inspected users "
        "and their follower/following list from the database."
        "\n"
        "\n"
        "Are you sure you want to continue?**",
        buttons=[
            [
                Button.inline("Confirm", "prune:1"),
                Button.inline("Cancel", "prune:0"),
            ]
        ],
    )
    raise events.StopPropagation


@bot.on(events.CallbackQuery(pattern="^ins:(\w[\w.]+):(\w[\w.]+)$"))
async def inspect_query(callback: CallbackQuery):
    inspector_username = callback.pattern_match.group(1).decode()
    user_username = callback.pattern_match.group(2).decode()

    user_already_exists = database.get.get_inspected_user(user_username)
    if user_already_exists:
        await callback.edit(
            "**This user is already under inspect.**",
            buttons=Button.clear(),
        )
        raise events.StopPropagation

    inspector = database.get.get_inspector(inspector_username)
    if not inspector:
        await callback.edit(
            f"**Inspector** `{inspector_username}` **does not exists.**",
            buttons=Button.clear(),
        )
        raise events.StopPropagation

    await callback.delete()
    wait_message: Message = await callback.respond(
        f"**Processing user** `{user_username}` "
        f"**with** `{inspector.username}`**...**",
        buttons=Button.clear(),
    )

    user = database.create.create_inspected_user(user_username, inspector)

    try:
        client = get_client(inspector.username)
    except Exception as e:
        logging.error(f"Error loging-in with {inspector.username}", exc_info=True)
        await callback.respond(f"Error loging-in with {inspector.username}:\n {e}")
        raise events.StopPropagation

    try:
        process_user(client, user, silent=True)
    except Exception as e:
        logging.error(f"Error processing user {user.username}", exc_info=True)
        await callback.respond(f"Error processing user {user.username}:\n {e}")
        raise events.StopPropagation

    user = database.get.get_inspected_user(user.username)
    await wait_message.delete()
    await callback.respond(
        f"✅ **User** `{user.username}` successfully proceeded.\n\n"
        f"**ID:** `{user.ig_pk}`\n"
        f"**Followers:** `{user.follower_count}`\n"
        f"**Followings:** `{user.following_count}`\n"
        f"\n"
        f"A list of all followers and followings have been added to database"
    )
    raise events.StopPropagation


@bot.on(events.CallbackQuery(pattern="^prune:([01])$"))
async def prune_database_query(callback: CallbackQuery):
    confirm = callback.pattern_match.group(1).decode()

    if confirm == "0":
        await callback.edit(
            "Pruning database has been canceled.", buttons=Button.clear()
        )

    if confirm == "1":
        database.delete.prune_database()
        await callback.edit("Database has been cleaned up.", buttons=Button.clear())

    raise events.StopPropagation


@bot.on(events.CallbackQuery(pattern="^reassign:(\d+):(\d+)$"))
async def reassign_inspected_user_query(callback: CallbackQuery):
    inspector_id = callback.pattern_match.group(1).decode()
    inspected_user_id = callback.pattern_match.group(2).decode()

    inspector = database.get.get_inspector(db_id=inspector_id)
    if not inspector:
        await callback.edit(
            f"**Inspector does not exists.**",
            buttons=Button.clear(),
        )
        raise events.StopPropagation

    inspected_user = database.get.get_inspected_user(db_id=inspected_user_id)
    if not inspected_user:
        await callback.edit(
            f"**Inspected user does not exists.**",
            buttons=Button.clear(),
        )
        raise events.StopPropagation

    inspected_user.inspector = inspector.id
    database.update.update_inspected_user(inspected_user)
    await callback.edit(
        f"**User** [{inspected_user.username}](https://instagram.com/{inspected_user.username}) "
        f"**has been successfully assigned to** `{inspector.username}`."
    )
    raise events.StopPropagation


@bot.on(events.CallbackQuery(pattern="^delu:(\d+):([01])$"))
async def delete_inspector_query(callback: CallbackQuery):
    inspected_user_id = callback.pattern_match.group(1).decode()
    confirm = callback.pattern_match.group(2).decode()

    inspected_user = database.get.get_inspected_user(db_id=inspected_user_id)
    if not inspected_user:
        await callback.edit(
            f"**User does not exists.**",
            buttons=Button.clear(),
        )
        raise events.StopPropagation

    if confirm == "0":
        await callback.edit(
            f"**Deletion of** `{inspected_user.username}` **has been canceled.**",
            buttons=Button.clear(),
        )
        raise events.StopPropagation

    if confirm == "1":
        database.delete.delete_inspected_user(inspected_user)
        await callback.edit(
            f"**User** `{inspected_user.username}` **has been deleted.**",
            buttons=Button.clear(),
        )
        raise events.StopPropagation


@bot.on(events.CallbackQuery(pattern="^del:(\w[\w.]+):?([01])?$"))
async def delete_inspector_query(callback: CallbackQuery):
    callback_data = callback.data.decode()
    inspector_username = callback.pattern_match.group(1).decode()
    confirm = callback.pattern_match.group(2)

    inspector = database.get.get_inspector(inspector_username)
    if not inspector:
        await callback.edit(
            f"**Inspector** `{inspector_username}` **does not exists.**",
            buttons=Button.clear(),
        )
        raise events.StopPropagation

    if confirm is None:
        await callback.edit(
            f"**Are you sure you want to delete** `{inspector.username}` **?**",
            buttons=[
                [
                    Button.inline("Delete", callback_data + ":1"),
                    Button.inline("Cancel", callback_data + ":0"),
                ]
            ],
        )
        raise events.StopPropagation

    confirm = confirm.decode()

    if confirm == "0":
        await callback.edit(
            f"**Deleting of** `{inspector.username}` **has been canceled.**",
            buttons=Button.clear(),
        )
        raise events.StopPropagation

    if confirm == "1":
        database.delete.delete_inspector(inspector)
        await callback.edit(
            f"**Inspector** `{inspector.username}` **has been deleted.**",
            buttons=Button.clear(),
        )
        raise events.StopPropagation


bot.loop.create_task(send_telegram_notifications(bot))
bot.loop.create_task(run_instagram())
bot.run_until_disconnected()
