from typing import TYPE_CHECKING

from core.database.get import (
    get_following,
    get_follower,
    get_inspector,
    get_inspected_user,
    get_all_inspectors,
    get_all_inspected_users,
)
from core.database.utils import Cursor
from core.datatypes import Inspector, UnderInspect

if TYPE_CHECKING:
    from core.datatypes import Follower, Following


def delete_follower(
    inspected_user: [int, "UnderInspect"], follower_ig_pk: int
) -> "Follower":
    if isinstance(inspected_user, UnderInspect):
        inspected_user = inspected_user.id

    follower = get_follower(inspected_user, follower_ig_pk)

    with Cursor() as cursor:
        cursor.execute(
            "DELETE FROM followers WHERE inspected_user=? AND ig_pk=?",
            (inspected_user, follower_ig_pk),
        )
        cursor.connection.commit()

    follower.id = None
    return follower


def delete_following(
    inspected_user: [int, "UnderInspect"], following_ig_pk: int
) -> "Following":
    if isinstance(inspected_user, UnderInspect):
        inspected_user = inspected_user.id

    following = get_following(inspected_user, following_ig_pk)

    with Cursor() as cursor:
        cursor.execute(
            "DELETE FROM followings WHERE inspected_user=? AND ig_pk=?",
            (inspected_user, following_ig_pk),
        )
        cursor.connection.commit()

    following.id = None
    return following


def delete_inspector(inspector: [str, Inspector]) -> Inspector:
    if isinstance(inspector, Inspector):
        inspector = inspector.username

    inspector_object = get_inspector(inspector)

    if inspector_object:
        with Cursor() as cursor:
            cursor.execute(
                "DELETE FROM inspectors WHERE username=?",
                (inspector,),
            )
            cursor.execute(
                "UPDATE under_inspect SET inspector=NULL WHERE inspector=?",
                (inspector_object.id,),
            )
            cursor.connection.commit()

    inspector_object.id = None
    return inspector_object


def delete_inspected_user(inspected_user: [str, UnderInspect]) -> UnderInspect:
    if isinstance(inspected_user, UnderInspect):
        inspected_user = inspected_user.username

    inspected_user_object = get_inspected_user(inspected_user)

    if inspected_user_object:
        with Cursor() as cursor:
            cursor.execute(
                "DELETE FROM under_inspect WHERE username=?",
                (inspected_user,),
            )
            cursor.execute(
                "DELETE FROM followers WHERE inspected_user=?",
                (inspected_user_object.id,),
            )
            cursor.execute(
                "DELETE FROM followings WHERE inspected_user=?",
                (inspected_user_object.id,),
            )
            cursor.connection.commit()

    inspected_user_object.id = None
    return inspected_user_object


def prune_database():
    inspectors = get_all_inspectors()
    inspectors_ids = list(map(lambda i: i.id, inspectors))

    inspected_users = get_all_inspected_users()

    for inspected_user in inspected_users:
        if inspected_user.inspector not in inspectors_ids:
            delete_inspected_user(inspected_user)
