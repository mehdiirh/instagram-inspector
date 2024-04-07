from typing import TYPE_CHECKING, Optional

from core.database import get
from core.database.utils import Cursor
from core.datatypes import TelegramMessage

if TYPE_CHECKING:
    from instagrapi.types import UserShort
    from core.datatypes import Follower, Following, UnderInspect


def create_follower_for_inspected_user(
    inspected_user: "UnderInspect",
    follower_details: "UserShort",
) -> Optional["Follower"]:

    follower_exist = get.get_follower(inspected_user, follower_details.pk)

    if not follower_exist:
        with Cursor() as cursor:
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
    inspected_user: "UnderInspect",
    following_details: "UserShort",
) -> Optional["Following"]:

    following_exist = get.get_following(inspected_user, following_details.pk)

    if not following_exist:
        with Cursor() as cursor:
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


def create_telegram_notification(
    text: str,
    media_url: str = None,
) -> TelegramMessage:
    with Cursor() as cursor:
        cursor.execute(
            "INSERT INTO telegram_message (text, media_url, status) VALUES (?, ?, ?)",
            (
                text,
                media_url,
                0,
            ),
        )
        cursor.connection.commit()

        return TelegramMessage(
            id=cursor.lastrowid, text=text, media_url=media_url, status=0
        )
