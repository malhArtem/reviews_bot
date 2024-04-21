from aiogram import BaseMiddleware, types
from aiogram.types import TelegramObject

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.types import Message
from cachetools import TTLCache
from db.models.users import Users


class CreateSessionMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        session_maker = data["session_maker"]
        print(handler)
        async with session_maker() as session:
            if isinstance(event, types.Message):
                await Users.add_user(event.from_user.id, event.chat.id, event.from_user.full_name, event.from_user.username, session)
            elif isinstance(event, types.CallbackQuery):
                await Users.add_user(event.from_user.id, event.message.chat.id, event.from_user.full_name,
                                     event.from_user.username, session)
            data["session"] = session
            return await handler(event, data)



class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, throttle_time_spin: int, throttle_time_other: int):
        self.caches = {
            "spin": TTLCache(maxsize=10_000, ttl=throttle_time_spin),
            "default": TTLCache(maxsize=10_000, ttl=throttle_time_other)
        }

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any],
    ) -> Any:
        throttling_key = get_flag(data, "throttling_key")
        if throttling_key is not None and throttling_key in self.caches:
            if event.chat.id in self.caches[throttling_key]:
                return
            else:
                self.caches[throttling_key][event.chat.id] = None
        return await handler(event, data)
