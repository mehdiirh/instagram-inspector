import json
from typing import TYPE_CHECKING

from instagrapi import Client

from core import database
from core.datatypes import UnderInspect

if TYPE_CHECKING:
    from instagrapi.types import User


def get_client(username: str = None, inspector_id: int = None):
    proxy_settings = database.get.get_setting(key="proxy")
    inspector = database.get.get_inspector(username=username, db_id=inspector_id)
    client = Client()

    if proxy_settings.active:
        client.set_proxy(proxy_settings.value)

    try:
        client.set_settings(json.loads(inspector.settings))
        client.login(inspector.username, inspector.password)
        client.login()
    except Exception:
        client.login(inspector.username, inspector.password)
        inspector.settings = json.dumps(client.get_settings())
        database.update.update_inspector(inspector)

    return client


def check_follower_following_count(inspected_user: UnderInspect, user_info: "User"):
    if inspected_user.follower_count != user_info.follower_count:
        # TODO: send notification
        pass

    if inspected_user.following_count != user_info.following_count:
        # TODO: notification
        pass


def main():
    inspectors = database.get.get_all_inspectors()

    for inspector in inspectors:
        client = get_client(inspector.username)
        under_inspect_users = database.get.get_inspector_inspected_users(inspector)

        for user in under_inspect_users:
            user_info = client.user_info_by_username_v1(user.username)
            check_follower_following_count(user, user_info)

            user_followers = client.user_followers_v1(user_info.pk)
            print(user_followers)
            print(len(user_followers))

            user_followings = client.user_following_v1(user_info.pk)
            print(user_followings)
            print(len(user_followings))


if __name__ == "__main__":
    main()
