from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.utils.filters import AdminFilter
from bot.utils.keyboard import TariffCallbackFactory
from db.models.tariffs import Tariffs
from utils.parse_texts import texts

router = Router()
router.message.filter(F.chat.type == "private")
router.callback_query.filter(F.message.chat.type == "private")

router.callback_query.filter(AdminFilter())
router.message.filter(AdminFilter())
class PricesStates(StatesGroup):
    input = State()


@router.callback_query(F.data == 'prices')
async def edit_prices(callback: types.CallbackQuery, session, state: FSMContext):
    await state.clear()
    tariffs = await Tariffs.get_tariffs(session)
    text = texts.price_edit_text
    builder = InlineKeyboardBuilder()
    for tariff in tariffs:

        builder.button(text=tariff.name, callback_data=TariffCallbackFactory(id=tariff.id, action="edit"))

    builder.button(text="Назад", callback_data="admin")
    builder.adjust(1)
    await callback.message.edit_text(text, reply_markup=builder.as_markup())


@router.callback_query(TariffCallbackFactory.filter(F.action == "edit"))
async def edit_prices(callback: types.CallbackQuery, callback_data: TariffCallbackFactory, state: FSMContext):
    await state.update_data(tariff_id=callback_data.id)
    await state.set_state(PricesStates.input)
    text = texts.price_input
    builder = InlineKeyboardBuilder()
    builder.button(text=texts.back_button, callback_data="prices")

    await callback.answer()
    await callback.message.edit_text(text, reply_markup=builder.as_markup())


@router.message(F.text, PricesStates.input)
async def edit_prices(message: types.Message, state: FSMContext, session):
    builder = InlineKeyboardBuilder()
    try:
        new_price = int(message.text)
    except ValueError:
        text = texts.price_input

        builder.button(text=texts.back_button, callback_data="prices")
        return await message.answer(text, reply_markup=builder.as_markup())

    builder.button(text="Да", callback_data="success_price")
    builder.button(text="Нет", callback_data="prices")
    text = texts.confirmation_edit
    await state.update_data(new_price=new_price)
    await message.answer(text, reply_markup=builder.as_markup())


@router.callback_query(F.data == "success_price")
async def edit_prices(callback: types.CallbackQuery, state: FSMContext, session):
    state_data = await state.get_data()
    tariff = await Tariffs.update_tariffs(state_data.get("tariff_id"), state_data.get("new_price"), session)
    text = f"Изменено премиум {tariff.name} \nстоимостью {state_data.get('new_price')} руб"
    builder = InlineKeyboardBuilder()
    builder.button(text="Назад", callback_data='admin')
    await callback.answer()
    await callback.message.edit_text(text, reply_markup=builder.as_markup())

