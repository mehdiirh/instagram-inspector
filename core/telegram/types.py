from typing import Union

from telethon.events import NewMessage, CallbackQuery
from telethon.tl.custom import Message, Conversation

Message = Union[NewMessage.Event, Message]
Conversation = Union[NewMessage.Event, Conversation]
CallbackQuery = CallbackQuery.Event
