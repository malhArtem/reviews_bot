import datetime
import enum

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from db.base import Base, created_at, updated_at

from sqlalchemy import ForeignKey, Enum, update, select

from sqlalchemy.orm import Mapped, mapped_column, relationship


class Tariffs(Base):
    __tablename__ = 'tariffs'

    id: Mapped[int] = mapped_column(primary_key=True)
    duration: Mapped[int]
    name: Mapped[str]
    price: Mapped[int]


    @staticmethod
    async def init_tariffs(session_maker: async_sessionmaker):
        async with session_maker() as session:
            async with session.begin():
                tariffs = await session.execute(select(Tariffs))
                tariffs = tariffs.scalars().all()
                if not tariffs:
                    tariffs = [
                        Tariffs(duration=3, name="На 3 дня", price=100),
                        Tariffs(duration=7, name="На 1 неделю", price=200),
                        Tariffs(duration=30, name="На 1 месяц", price=800)
                    ]
                    session.add_all(tariffs)

    @staticmethod
    async def update_tariffs(id, price, session: AsyncSession):
        async with session.begin():
            stmt = update(Tariffs).values(price=price).filter(Tariffs.id == id).returning(Tariffs)
            result = await session.execute(stmt)
            return result.scalars().first()
    @staticmethod
    async def get_tariffs(session: AsyncSession):
        stmt = select(Tariffs).order_by(Tariffs.id)
        result = await session.execute(stmt)
        tariffs = result.scalars().all()
        return tariffs

    @staticmethod
    async def get_tariff(id, session: AsyncSession):
        tariff = await session.get(Tariffs, id)
        return tariff
