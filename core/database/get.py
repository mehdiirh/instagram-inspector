from typing import Literal

from core.database.utils import dataclass_wrapper, Cursor
from core.datatypes import (
    Follower,
    Following,
    Inspector,
    UnderInspect,
    TelegramMessage,
    Setting,
)


@dataclass_wrapper(Inspector)
def get_all_inspectors() -> list[Inspector]:
    with Cursor(close_on_exit=False) as cursor:
        return cursor.execute(
            "SELECT id, username, password, settings, ig_pk FROM inspectors"
        )


@dataclass_wrapper(Inspector, fetchone=True)
def get_inspector(username: str = None, db_id: int = None) -> Inspector:
    with Cursor(close_on_exit=False) as cursor:
        return cursor.execute(
            "SELECT id, username, password, settings, ig_pk "
            "FROM inspectors WHERE (username LIKE ? OR id = ?)",
            (username, db_id),
        )


@dataclass_wrapper(UnderInspect, fetchone=True)
def get_inspected_user(username: str = None, db_id: int = None) -> UnderInspect:
    with Cursor(close_on_exit=False) as cursor:
        return cursor.execute(
            "SELECT id, username, following_count, follower_count, ig_pk, inspector"
            " FROM under_inspect WHERE (username LIKE ? OR id = ?)",
            (username, db_id),
        )


@dataclass_wrapper(UnderInspect)
def get_inspector_inspected_users(inspector: [int, Inspector]) -> list[UnderInspect]:
    if isinstance(inspector, Inspector):
        inspector = inspector.id

    with Cursor(close_on_exit=False) as cursor:
        return cursor.execute(
            "SELECT id, username, following_count, follower_count, ig_pk, inspector "
            "FROM under_inspect WHERE inspector=?",
            (inspector,),
        )


@dataclass_wrapper(Follower, fetchone=True)
def get_follower(inspected_user: [int, UnderInspect], follower_ig_pk: int) -> Follower:
    if isinstance(inspected_user, UnderInspect):
        inspected_user = inspected_user.id

    with Cursor(close_on_exit=False) as cursor:
        return cursor.execute(
            "SELECT id, ig_pk, username, inspected_user FROM followers WHERE inspected_user=? AND ig_pk=?",
            (inspected_user, follower_ig_pk),
        )


@dataclass_wrapper(Follower)
def fetch_followers(inspected_user: [int, UnderInspect]) -> list[Follower]:
    if isinstance(inspected_user, UnderInspect):
        inspected_user = inspected_user.id

    with Cursor(close_on_exit=False) as cursor:
        return cursor.execute(
            "SELECT id, ig_pk, username, inspected_user FROM followers WHERE inspected_user=?",
            (inspected_user,),
        )


@dataclass_wrapper(Following, fetchone=True)
def get_following(
    inspected_user: [int, UnderInspect], following_ig_pk: int
) -> Follower:
    if isinstance(inspected_user, UnderInspect):
        inspected_user = inspected_user.id

    with Cursor(close_on_exit=False) as cursor:
        return cursor.execute(
            "SELECT id, ig_pk, username, inspected_user FROM followings WHERE inspected_user=? AND ig_pk=?",
            (inspected_user, following_ig_pk),
        )


@dataclass_wrapper(Following)
def fetch_followings(inspected_user: [int, UnderInspect]) -> list[Following]:
    if isinstance(inspected_user, UnderInspect):
        inspected_user = inspected_user.id

    with Cursor(close_on_exit=False) as cursor:
        return cursor.execute(
            "SELECT id, ig_pk, username, inspected_user FROM followings WHERE inspected_user=?",
            (inspected_user,),
        )


@dataclass_wrapper(TelegramMessage)
def telegram_messages(status: Literal[0, 1] = None) -> list[TelegramMessage]:
    with Cursor(close_on_exit=False) as cursor:
        if status is None:
            return cursor.execute(
                "SELECT id, text, media_url, status FROM telegram_message"
            )
        else:
            return cursor.execute(
                "SELECT id, text, media_url, status FROM telegram_message WHERE status=?",
                str(status),
            )


@dataclass_wrapper(Setting, fetchone=True)
def get_setting(key: str) -> Setting:
    with Cursor(close_on_exit=False) as cursor:
        return cursor.execute(
            "SELECT id, active, `key`, value FROM settings WHERE `key`=?", (key,)
        )
