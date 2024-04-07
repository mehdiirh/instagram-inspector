from asyncio import sleep

from telethon import TelegramClient

from core import settings
from core.database.get import telegram_messages
from core.database.update import update_telegram_message


async def send_telegram_notifications(bot: TelegramClient):
    while True:
        new_messages = telegram_messages(status=0)
        for message in new_messages:
            await bot.send_message(
                int(settings.TELEGRAM_LOG_CHANNEL),
                message.text,
                file=message.media_url,
                parse_mode="html",
            )

            message.status = 1
            update_telegram_message(message)
            await sleep(3)

        await sleep(10)
