from aiogram import Router, types, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.handlers.users.pay.crypto_pay import create_invoice
from bot.utils.filters import AgreeFilter, PremiumFilter
from db.models.reviews import Reviews
from db.models.tariffs import Tariffs
from db.models.users import Users

from bot.utils.keyboard import ReviewsCallbackFactory, TariffCallbackFactory, ProfileCallbackFactory
from utils.parse_texts import texts

router = Router()
router.message.filter(F.chat.type == "private")
router.callback_query.filter(F.message.chat.type == "private")

router.message.filter(AgreeFilter())
router.callback_query.filter(AgreeFilter())


@router.callback_query(F.data == "premium")
async def premium(callback: types.CallbackQuery, session):
    tariffs = await Tariffs.get_tariffs(session)
    # await create_invoice(callback.from_user.id, 300, callback.bot)
    text = texts.buy_tariff
    builder = InlineKeyboardBuilder()
    for tariff in tariffs:

        builder.button(text=tariff.name, callback_data=TariffCallbackFactory(id=tariff.id))
    builder.button(text="Проверить платежи", callback_data='check_payments')
    builder.button(text=texts.back_button, callback_data=ProfileCallbackFactory(user_id=str(callback.from_user.id)))
    builder.adjust(1)

    await callback.answer()
    await callback.message.edit_text(text, reply_markup=builder.as_markup())


@router.callback_query(F.data == "back_premium")
async def premium(callback: types.CallbackQuery, session):
    tariffs = await Tariffs.get_tariffs(session)

    text = texts.buy_tariff
    builder = InlineKeyboardBuilder()
    for tariff in tariffs:

        builder.button(text=tariff.name, callback_data=TariffCallbackFactory(id=tariff.id))
    builder.button(text="Проверить платежи", callback_data='check_payments')
    builder.button(text="Назад", callback_data=ProfileCallbackFactory(user_id=str(callback.from_user.id)))
    builder.adjust(1)

    await callback.answer()
    await callback.message.answer(text, reply_markup=builder.as_markup())
    await callback.message.delete()


@router.callback_query(TariffCallbackFactory.filter(F.action == 'look'))
async def premium(callback: types.CallbackQuery, callback_data: TariffCallbackFactory, state: FSMContext):
    await state.update_data(tariff_id=callback_data.id)
    builder = InlineKeyboardBuilder()
    builder.button(text="ЮKassa", callback_data='kassa')
    builder.button(text="Crypto bot", callback_data='crypto_bot')

    builder.button(text="Назад", callback_data='back_premium')
    builder.adjust(1)
    text = texts.buy_payment_system

    await callback.answer()
    if callback.message.invoice:
        await callback.message.answer(text, reply_markup=builder.as_markup())
        await callback.message.delete()
    else:
        await callback.message.edit_text(text, reply_markup=builder.as_markup())