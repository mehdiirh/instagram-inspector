import logging
from asyncio import sleep

from core import database
from instagram.utils import (
    get_client,
    save_follower_following_count_changes,
    save_follower_changes,
    save_following_changes,
)
from telegram import messages


def process_user(client, user, silent=False):
    user_info = client.user_info_by_username_v1(user.username)
    user.ig_pk = user_info.pk
    save_follower_following_count_changes(user, user_info, silent=silent)

    user_followers = []
    for _ in range(3):
        _user_followers = client.user_followers_v1(user_info.pk)
        user_followers += _user_followers
        user_followers = list(set(user_followers))

        if len(user_followers) == user_info.follower_count:
            break

    save_follower_changes(user, user_followers, silent=silent)

    user_followings = []
    for _ in range(3):
        _user_followings = client.user_following_v1(user_info.pk)
        user_followings += _user_followings
        user_followings = list(set(user_followings))

        if len(user_followings) == user_info.following_count:
            break

    save_following_changes(user, user_followings, silent=silent)


def main():
    inspectors = database.get.get_all_inspectors()

    for inspector in inspectors:
        try:
            client = get_client(inspector.username)
        except Exception as err:
            messages.error_log(
                stage=f"Loging-in with user: <code>{inspector.username}</code>",
                exception=err,
                save=True,
            )
            continue

        under_inspect_users = database.get.get_inspector_inspected_users(inspector)

        for user in under_inspect_users:
            process_user(client, user, silent=False)


async def run_instagram():
    print("[✓] Instagram Inspector Started.")
    while True:
        try:
            main()
        except Exception as e:
            logging.error(f"Error in processing instagram: {e}", exc_info=True)
            messages.error_log("Instagram processing", exception=e, save=True)

        await sleep(30 * 60)
