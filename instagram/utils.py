import json
from typing import TYPE_CHECKING

from instagrapi import Client

from core import database
from core.datatypes import UnderInspect

if TYPE_CHECKING:
    from instagrapi.types import User, UserShort


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
        inspector.ig_pk = client.user_id
        database.update.update_inspector(inspector)

    return client


def get_user_short_object_by_pk(
    user_list: list["UserShort"], pk: [int, str]
) -> "UserShort":
    user = list(filter(lambda u: str(u.pk) == str(pk), user_list))
    if user:
        return user[0]
    return


def save_follower_following_count_changes(
    inspected_user: UnderInspect, user_info: "User"
):
    if inspected_user.follower_count != user_info.follower_count:
        # TODO: send notification
        pass

    if inspected_user.following_count != user_info.following_count:
        # TODO: notification
        pass

    inspected_user.follower_count = user_info.follower_count
    inspected_user.following_count = user_info.following_count
    database.update.update_inspected_user(inspected_user)


def save_follower_changes(
    inspected_user: UnderInspect,
    user_follower_list: list["UserShort"],
) -> None:
    saved_followers = database.get.fetch_followers(inspected_user)

    saved_followers_pks = list(map(lambda x: str(x.ig_pk), saved_followers))
    fresh_followers_pks = list(map(lambda x: str(x.pk), user_follower_list))

    new_followers = set(fresh_followers_pks) - set(saved_followers_pks)
    new_unfollows = set(saved_followers_pks) - set(fresh_followers_pks)

    for follower in new_followers:
        # TODO: Send notification
        follower_details = get_user_short_object_by_pk(user_follower_list, follower)
        database.create.create_follower_for_inspected_user(
            inspected_user, follower_details
        )

    for unfollow in new_unfollows:
        # TODO: Send notification
        # TODO: delete follower from db
        pass


def save_following_changes(
    inspected_user: UnderInspect,
    user_following_list: list["UserShort"],
) -> None:
    saved_followings = database.get.fetch_followings(inspected_user)

    saved_followings_pks = list(map(lambda x: str(x.ig_pk), saved_followings))
    fresh_followings_pks = list(map(lambda x: str(x.pk), user_following_list))

    new_followings = set(fresh_followings_pks) - set(saved_followings_pks)
    new_unfollows = set(saved_followings_pks) - set(fresh_followings_pks)

    for follower in new_followings:
        # TODO: Send notification
        follower_details = get_user_short_object_by_pk(user_following_list, follower)
        database.create.create_following_for_inspected_user(
            inspected_user, follower_details
        )

    for unfollow in new_unfollows:
        # TODO: Send notification
        # TODO: delete follower from db
        pass
