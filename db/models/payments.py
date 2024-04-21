from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from db.base import Base, created_at

from sqlalchemy.orm import Mapped, mapped_column, relationship


class Payments(Base):
    __tablename__ = 'payments'

    id: Mapped[int] = mapped_column(primary_key=True)
    provider: Mapped[str]
    payment_id: Mapped[str]
    user_id: Mapped[str]
    price: Mapped[int]
    status: Mapped[str] = mapped_column(default="active")
    created_at: Mapped[created_at]



    @staticmethod
    async def add_payment(payment_id, provider, user_id, price, status, session: AsyncSession):
        payment = Payments(payment_id=str(payment_id),
                           provider=provider,
                           user_id=str(user_id),
                           price=price,
                           status=status)

        session.add(payment)
        await session.commit()

    @staticmethod
    async def get_payment(payment_id, provider, session: AsyncSession):
        stmt = select(Payments).filter(Payments.provider == provider).filter(Payments.payment_id == str(payment_id))
        result = await session.execute(stmt)
        return result.scalars().first()


    @staticmethod
    async def update_payment(id, session: AsyncSession):
        stmt = update(Payments).filter(Payments.id == id).values(status='paid')
        await session.execute(stmt)
        await session.commit()


    @staticmethod
    async def update_payment_payment_id(payment_id, session: AsyncSession):
        stmt = update(Payments).filter(Payments.payment_id == str(payment_id)).filter(Payments.provider == 'crypto_bot').values(status='paid')
        await session.execute(stmt)
        await session.commit()


    @staticmethod
    async def get_user_active_payments(user_id, session: AsyncSession):
        stmt = select(Payments.payment_id).filter(Payments.user_id == user_id).filter(Payments.status == 'active')
        result = await session.execute(stmt)
        return result.scalars().all()