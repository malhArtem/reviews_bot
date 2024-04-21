import datetime

from aiogram import types
from aiogram.filters import BaseFilter
from aiogram.types import Message, TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession

from bot.utils.config_reader import config
from db.models.users import Users


admin_id = config.admin_id


class AgreeFilter(BaseFilter):
    async def __call__(self, event: types.Message, session_maker) -> bool:
        async with session_maker() as session:
            agree = await Users.get_user_agree(event.from_user.id, session)

        return agree


class BlockedFilter(BaseFilter):
    async def __call__(self, event: types.Message, session_maker) -> bool:
        async with session_maker() as session:
            blocked = await Users.get_user_blocked(event.from_user.id, session)

        return not blocked



class PremiumFilter(BaseFilter):
    async def __call__(self, event: TelegramObject, session_maker) -> bool:
        async with session_maker() as session:
            user = await Users.get_user(event.from_user.id, session)
        now = datetime.datetime.utcnow()
        return user.premium is not None and (user.premium > now)


class AdminFilter(BaseFilter):
    async def __call__(self, event: TelegramObject, session_maker) -> bool:
        if str(event.from_user.id) == config.admin_id:
            return True
        async with session_maker() as session:
            user = await Users.get_user(event.from_user.id, session)
            return user.is_admin
