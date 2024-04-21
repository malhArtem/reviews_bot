from sqlalchemy.ext.asyncio import AsyncSession

from db.base import Base, created_at

from sqlalchemy.orm import Mapped, mapped_column, relationship


class Advertisements(Base):
    __tablename__ = 'advertisements'

    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(nullable=True)
    photo: Mapped[str] = mapped_column(nullable=True)
    button: Mapped[str] = mapped_column(nullable=True)
    created_at: Mapped[created_at]


    @staticmethod
    async def add_advertisements(session: AsyncSession, photo=None, button=None, text=None):
        advertisement = Advertisements(text=text,
                                       photo=photo,
                                       button=button)

        session.add(advertisement)
        await session.commit()


