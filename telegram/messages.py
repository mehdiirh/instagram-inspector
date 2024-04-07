from functools import wraps
from pathlib import Path
from typing import TYPE_CHECKING

from core import database
from core.datatypes import TelegramMessage

if TYPE_CHECKING:
    from core.datatypes import UnderInspect, Follower, Following


MESSAGES_BASE_PATH = Path(__file__).parent / "message_templates"


def render_template(template_name: str, context: dict = None):
    if context is None:
        context = {}

    with open(MESSAGES_BASE_PATH / template_name, "r") as template:
        template_content = template.read().strip()
        return template_content.format(**context)


def db_control(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        insert_to_db = kwargs.pop("save", False)
        text = fn(*args, **kwargs)
        if insert_to_db:
            return database.create.create_telegram_notification(text)
        return TelegramMessage(id=None, text=text, status=0)

    return wrapper


@db_control
def follower_count_change(
    inspected_user: "UnderInspect",
    old_follower_count: int,
    new_follower_count: int,
) -> TelegramMessage:
    template = "follower_count_change.html"
    change_type = (
        "increased" if new_follower_count > old_follower_count else "decreased"
    )

    context = {
        "inspected_user_username": inspected_user.username,
        "change_type": change_type,
        "old_follower_count": old_follower_count,
        "new_follower_count": new_follower_count,
    }

    return render_template(template, context)


@db_control
def following_count_change(
    inspected_user: "UnderInspect",
    old_following_count: int,
    new_following_count: int,
) -> TelegramMessage:
    template = "following_count_change.html"
    change_type = (
        "increased" if new_following_count > old_following_count else "decreased"
    )

    context = {
        "inspected_user_username": inspected_user.username,
        "change_type": change_type,
        "old_following_count": old_following_count,
        "new_following_count": new_following_count,
    }

    return render_template(template, context)


@db_control
def new_follower(
    inspected_user: "UnderInspect",
    new_follower_object: "Follower",
) -> TelegramMessage:
    template = "new_follower.html"

    context = {
        "inspected_user_username": inspected_user.username,
        "new_follower_username": new_follower_object.username,
    }

    return render_template(template, context)


@db_control
def new_following(
    inspected_user: "UnderInspect",
    new_following_object: "Follower",
) -> TelegramMessage:
    template = "new_following.html"

    context = {
        "inspected_user_username": inspected_user.username,
        "new_following_username": new_following_object.username,
    }

    return render_template(template, context)


@db_control
def new_unfollow(
    inspected_user: "UnderInspect",
    new_unfollow_object: "Following",
) -> TelegramMessage:
    template = "new_unfollow.html"

    context = {
        "inspected_user_username": inspected_user.username,
        "new_unfollow_username": new_unfollow_object.username,
    }

    return render_template(template, context)


@db_control
def new_unfollowed_by(
    inspected_user: "UnderInspect",
    new_unfollower_object: "Follower",
) -> TelegramMessage:
    template = "new_unfollowed_by.html"

    context = {
        "inspected_user_username": inspected_user.username,
        "new_unfollower_username": new_unfollower_object.username,
    }

    return render_template(template, context)
