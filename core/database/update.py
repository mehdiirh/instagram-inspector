from core.database.utils import Cursor
from core.datatypes import Inspector, TelegramMessage, UnderInspect


def update_inspector(inspector_object: Inspector):
    with Cursor() as cursor:
        cursor.execute(
            "UPDATE inspectors SET username=?, password=?, settings=?, ig_pk=? WHERE id=?",
            (
                inspector_object.username,
                inspector_object.password,
                inspector_object.settings,
                inspector_object.ig_pk,
                inspector_object.id,
            ),
        )
        cursor.connection.commit()

    return inspector_object


def update_inspected_user(inspected_user: UnderInspect):
    with Cursor() as cursor:
        cursor.execute(
            "UPDATE under_inspect "
            "SET username=?, follower_count=?, following_count=?, ig_pk=?, inspector=? "
            "WHERE id=?",
            (
                inspected_user.username,
                inspected_user.follower_count,
                inspected_user.following_count,
                inspected_user.ig_pk,
                inspected_user.inspector,
                inspected_user.id,
            ),
        )
        cursor.connection.commit()


def update_telegram_message(telegram_message: TelegramMessage):
    with Cursor() as cursor:
        cursor.execute(
            "UPDATE telegram_message SET text=?, media_url=?, status=? WHERE id=?",
            (
                telegram_message.text,
                telegram_message.media_url,
                1 if bool(telegram_message.status) else 0,
                telegram_message.id,
            ),
        )
        cursor.connection.commit()
