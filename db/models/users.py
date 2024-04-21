import decimal
from sqlalchemy.ext.asyncio import async_sessionmaker, async_session, AsyncSession

from db.base import Base, created_at, updated_at
import datetime
import enum
from typing import Annotated, Optional
from sqlalchemy import (
    TIMESTAMP,
    CheckConstraint,
    Column,
    Enum,
    ForeignKey,
    Index,
    Integer,
    MetaData,
    PrimaryKeyConstraint,
    String,
    Table,
    text, select, func, exc,
)

from sqlalchemy.orm import Mapped, mapped_column, relationship, joinedload, selectinload, aliased

from db.models.reviews import Reviews
from pydantic import BaseModel


class User_with_rating():
    def __init__(self, user: tuple):
        self.user_id: str = user[0]
        self.chat_id: str = user[1]
        self.name: str = user[2]
        self.username: str | None = user[3]
        self.premium: datetime.datetime = user[4]
        self.about: str = user[5]
        self.is_admin: bool = user[6]
        self.is_blocked: bool = user[7]
        self.created_at: datetime.datetime = user[8]

        self.rating = round(decimal.Decimal(user[9]), 1) if user[9] is not None else None
        self.count_reviews = user[10]
        print(self.rating)




# таблица users в БД
class Users(Base):
    __tablename__ = 'users'

    user_id: Mapped[str] = mapped_column(primary_key=True)
    chat_id: Mapped[str]
    name: Mapped[str]
    username: Mapped[str] = mapped_column(nullable=True)

    premium: Mapped[datetime.datetime] = mapped_column(nullable=True)
    agree: Mapped[bool] = mapped_column(default=False)
    about: Mapped[str] = mapped_column(nullable=True)
    is_admin: Mapped[bool] = mapped_column(default=False)
    is_blocked: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

    # reviews_about: Mapped[list["Reviews"]] = relationship(back_populates="about")
    left_reviews: Mapped[list["Reviews"]] = relationship(back_populates="reviewer")

    @staticmethod
    async def add_user(user_id, chat_id, name, username, session: AsyncSession):
        user = Users(user_id=str(user_id), chat_id=str(chat_id), name=name, username=username)
        try:
            await session.merge(user)
            await session.commit()
        except exc.IntegrityError as e:
            print(e)

    @staticmethod
    async def get_users(session: AsyncSession):
        stmt = select(Users.user_id)
        result = await session.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def get_user(user_id, session: AsyncSession):
        u = aliased(Users)
        r = aliased(Reviews)
        stmt1 = select(u, r).filter(u.user_id == str(user_id)).join(r, u.user_id == r.about_id, isouter=True).subquery()
        print(stmt1)
        stmt2 = select(stmt1.c.user_id, stmt1.c.chat_id, stmt1.c.name, stmt1.c.username, stmt1.c.premium, stmt1.c.about, stmt1.c.is_admin, stmt1.c.is_blocked, stmt1.c.created_at, func.avg(stmt1.c.evaluation).over(partition_by=stmt1.c.user_id), func.count(stmt1.c.evaluation).over(partition_by=stmt1.c.user_id))
        print(stmt2)
        result = await session.execute(stmt2)
        user = result.unique().one_or_none()
        print(user)
        return User_with_rating(user) if user is not None else None

    @staticmethod
    async def get_user_agree(user_id, session: AsyncSession):
        stmt = select(Users.agree).filter(Users.user_id == str(user_id))
        return (await session.execute(stmt)).scalar_one_or_none()


    @staticmethod
    async def get_user_blocked(user_id, session: AsyncSession):
        stmt = select(Users.is_blocked).filter(Users.user_id == str(user_id))
        return (await session.execute(stmt)).scalar_one_or_none()


    @staticmethod
    async def update_user(user_id, session: AsyncSession, name=None, username=None, agree=None, premium=None, about=None, is_admin=None, is_blocked=None):
        user = await session.get(Users, str(user_id))
        if premium is not None:
            if user.premium is None or datetime.datetime.utcnow() > user.premium:
                premium = datetime.datetime.utcnow() + premium
            else:
                premium = user.premium + premium

        print(premium)

        if user is not None:
            user.agree = agree if agree is not None else user.agree
            user.premium = premium if premium is not None else user.premium
            user.about = about if about is not None else user.about
            user.name = name if name is not None else user.name
            user.username = username if username is not None else user.username
            user.is_admin = is_admin if is_admin is not None else user.is_admin
            user.is_blocked = is_blocked if is_blocked is not None else user.is_blocked

        await session.commit()

    @staticmethod
    async def get_user_reviews(user_id, session: AsyncSession, offset=0, limit=3):
        # query = (select(Users)
        #          .filter(Users.user_id == str(user_id))
        #          .options(joinedload(Users.reviews_about)))

        stmt = select(Reviews).filter(Reviews.about_id == str(user_id)).order_by(Reviews.created_at.desc()).slice(offset, offset + limit + 1).options(joinedload(Reviews.reviewer))
        stmt2 = select(func.count(Reviews.id)).filter(Reviews.about_id == str(user_id))
        reviews = await session.execute(stmt)
        pages = await session.execute(stmt2)
        return reviews.scalars().all(), pages.scalar_one_or_none() // 3 + 1


    @staticmethod
    async def get_user_with_reviews_by_username(username, session: AsyncSession):
        u = aliased(Users)
        r = aliased(Reviews)
        print(username)
        stmt = (select(u).filter(u.username == username).subquery())
        stmt0 = select(stmt).order_by(stmt.c.updated_at.desc()).limit(1).subquery()
        stmt1 = select(stmt0, r).join(r, stmt0.c.user_id == r.about_id, isouter=True)
        print(stmt1)
        stmt2 = select(stmt1.c.user_id, stmt1.c.chat_id, stmt1.c.name, stmt1.c.username, stmt1.c.premium, stmt1.c.about, stmt1.c.is_admin,
                       stmt1.c.is_blocked, stmt1.c.created_at, func.avg(stmt1.c.evaluation).over(partition_by=stmt1.c.user_id),
                       func.count(stmt1.c.evaluation).over(partition_by=stmt1.c.user_id))

        print(stmt2)
        result = await session.execute(stmt2)
        user = result.unique().one_or_none()
        print(user)
        return User_with_rating(user) if user is not None else None


        #
        # res = await session.execute(query)
        # result: Users = res.unique().scalars().one()
        #
        # return result
