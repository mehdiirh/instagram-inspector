from dataclasses import dataclass
from typing import Literal, Optional


@dataclass
class Inspector:
    id: int
    username: str
    password: str
    settings: str
    ig_pk: Optional[int] = None


@dataclass
class UnderInspect:
    id: int
    username: str
    inspector: int
    following_count: int = 0
    follower_count: int = 0
    ig_pk: Optional[int] = None


@dataclass
class Follower:
    id: int
    ig_pk: int
    inspected_user: int


@dataclass
class Following:
    id: int
    ig_pk: int
    inspected_user: int


@dataclass
class TelegramMessage:
    id: int
    text: str
    status: Literal[0, 1]
    media_url: Optional[str] = None


@dataclass
class Setting:
    id: int
    active: bool
    key: str
    value: str

    def __post_init__(self):
        self.active = bool(self.active)
