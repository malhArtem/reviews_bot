import datetime

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.advertisements import Advertisements
from db.models.reviews import Reviews
from db.models.users import Users


class Statistics:

    @staticmethod
    async def get_stats(session: AsyncSession):
        stmt = select(select(func.count(Users.user_id),
                             func.count(Users.user_id).filter(Users.premium > datetime.datetime.utcnow())).subquery(),
                      select(func.count(Advertisements.id)).subquery(),
                      select(func.count(Reviews.id)).subquery())


        result = await session.execute(stmt)
        stat = result.first()
        print(stat[0], stat[1], stat[2], stat[3])
        return stat