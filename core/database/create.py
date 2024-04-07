from typing import TYPE_CHECKING

from core.database import get
from core.database.utils import Cursor
from core.datatypes import UnderInspect, Follower, Following

if TYPE_CHECKING:
    from instagrapi.types import UserShort


def create_follower_for_inspected_user(
    inspected_user: UnderInspect, follower_details: "UserShort"
) -> Follower:
    with Cursor(close_on_exit=False) as cursor:
        does_exist = get.get_follower(inspected_user, follower_details.pk)

        if not does_exist:
            cursor.execute(
                "INSERT INTO followers (ig_pk, inspected_user, username) VALUES (?, ?, ?)",
                (
                    follower_details.pk,
                    inspected_user.id,
                    follower_details.username,
                ),
            )
            cursor.connection.commit()

        return get.get_follower(inspected_user, follower_details.pk)


def create_following_for_inspected_user(
    inspected_user: UnderInspect, following_details: "UserShort"
) -> Following:
    with Cursor(close_on_exit=False) as cursor:
        does_exist = get.get_following(inspected_user, following_details.pk)

        if not does_exist:
            cursor.execute(
                "INSERT INTO followings (ig_pk, inspected_user, username) VALUES (?, ?, ?)",
                (
                    following_details.pk,
                    inspected_user.id,
                    following_details.username,
                ),
            )
            cursor.connection.commit()

        return get.get_following(inspected_user, following_details.pk)
