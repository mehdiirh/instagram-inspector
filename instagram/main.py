from core import database
from instagram.utils import (
    get_client,
    save_follower_following_count_changes,
    save_follower_changes,
    save_following_changes,
)


def main():
    inspectors = database.get.get_all_inspectors()

    for inspector in inspectors:
        client = get_client(inspector.username)
        under_inspect_users = database.get.get_inspector_inspected_users(inspector)

        for user in under_inspect_users:
            user_info = client.user_info_by_username_v1(user.username)
            user.ig_pk = user_info.pk
            save_follower_following_count_changes(user, user_info)

            user_followers = client.user_followers_v1(user_info.pk)
            save_follower_changes(user, user_followers)

            user_followings = client.user_following_v1(user_info.pk)
            save_following_changes(user, user_followings)


if __name__ == "__main__":
    main()
