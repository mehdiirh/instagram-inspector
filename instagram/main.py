import logging
from time import sleep

from core import database, settings
from instagram.utils import (
    get_client,
    save_follower_following_count_changes,
    save_follower_changes,
    save_following_changes,
)
from telegram import messages

logging.basicConfig(
    filename=settings.BASE_DIR / "logs/instagram.log",
    filemode="a",
    format="[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d - %H:%M:%S",
    level=logging.WARNING,
)


def process_user(client, user, silent=False):
    user_info = client.user_info_by_username_v1(user.username)
    user.ig_pk = user_info.pk
    save_follower_following_count_changes(user, user_info, silent=silent)

    user_followers = client.user_followers_v1(user_info.pk)
    save_follower_changes(user, user_followers, silent=silent)

    user_followings = client.user_following_v1(user_info.pk)
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
            )
            continue

        under_inspect_users = database.get.get_inspector_inspected_users(inspector)

        for user in under_inspect_users:
            process_user(client, user, silent=False)


if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as e:
            logging.error(f"Error in processing instagram: {e}", exc_info=True)
            messages.error_log("Instagram processing", exception=e)

        sleep(30 * 60)
