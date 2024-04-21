import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from db.base import Base, created_at, updated_at

from sqlalchemy import ForeignKey, delete, select, func

from sqlalchemy.orm import Mapped, mapped_column, relationship


class Reviews(Base):
    __tablename__ = 'reviews'

    id: Mapped[int] = mapped_column(primary_key=True)
    reviewer_id: Mapped[str] = mapped_column(ForeignKey("users.user_id"))
    about_id: Mapped[str]
    evaluation: Mapped[int]
    text: Mapped[str]
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

    repr_cols = ("text", )
    # about: Mapped["Users"] = relationship(back_populates="reviews_about",
    #                                       primaryjoin="Reviews.about_id == Users.user_id")
    reviewer: Mapped["Users"] = relationship(back_populates="left_reviews",
                                             primaryjoin="Reviews.reviewer_id == Users.user_id")

    @staticmethod
    async def add_review(reviewer_id, about_user, evaluation, review_text, session: AsyncSession):
        async with session.begin():
            review = Reviews(reviewer_id=str(reviewer_id),
                             about_id=about_user,
                             evaluation=evaluation,
                             text=review_text)

            session.add(review)

    @staticmethod
    async def get_review(id, session):
        async with session.begin():
            review = await session.get(Reviews, id)
            return review


    @staticmethod
    async def clear_user_reviews(user_id, session: AsyncSession):
        async with session.begin():
            stmt = delete(Reviews).filter(Reviews.about_id == str(user_id))
            await session.execute(stmt)


    @staticmethod
    async def get_today_user_reviews(user_id, session: AsyncSession):
        stmt = select(func.count(Reviews.id)).filter(Reviews.reviewer_id == str(user_id)).filter(Reviews.created_at < datetime.datetime.today())
        count = await session.execute(stmt)
        return count.scalar()


    @staticmethod
    async def get_review_about(author_id, about_id, session):
        stmt = select(Reviews).filter(Reviews.reviewer_id == str(author_id)).filter(Reviews.about_id == str(about_id))
        result = await session.execute(stmt)
        return result.scalars().one_or_none()