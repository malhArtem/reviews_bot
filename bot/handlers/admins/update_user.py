import datetime

from aiogram import Router, F, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.utils.filters import AdminFilter
from bot.utils.keyboard import TariffCallbackFactory
from db.models.reviews import Reviews
from db.models.tariffs import Tariffs
from db.models.users import Users
from utils.parse_texts import texts

router = Router()
router.message.filter(F.chat.type == "private")
router.callback_query.filter(F.message.chat.type == "private")
router.callback_query.filter(AdminFilter())
router.message.filter(AdminFilter())

class UpdateUser(StatesGroup):
    add_admin = State()
    clear_reviews = State()
    give_premium = State()
    block = State()


async def update_user_helper():
    text = texts.input_user_text
    builder = InlineKeyboardBuilder()
    builder.button(text=texts.back_button, callback_data="admin")
    return text, builder


@router.callback_query(F.data == "add_admin")
async def add_admin(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(UpdateUser.add_admin)
    text, builder = await update_user_helper()
    await callback.message.edit_text(text, reply_markup=builder.as_markup())


@router.callback_query(F.data == "block")
async def add_admin(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(UpdateUser.block)
    text, builder = await update_user_helper()
    await callback.message.edit_text(text, reply_markup=builder.as_markup())


@router.callback_query(F.data == "give_premium")
async def add_admin(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(UpdateUser.give_premium)
    text, builder = await update_user_helper()
    await callback.message.edit_text(text, reply_markup=builder.as_markup())


@router.callback_query(F.data == "clear_reviews")
async def add_admin(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(UpdateUser.clear_reviews)
    text, builder = await update_user_helper()
    await callback.message.edit_text(text, reply_markup=builder.as_markup())


@router.message(StateFilter(UpdateUser), F.text)
async def update_user(message: types.Message, state: FSMContext, session):
    builder = InlineKeyboardBuilder()
    user = None
    if message.entities is not None:
        for entity in message.entities:
            if entity.type == "mention":
                user = await Users.get_user_with_reviews_by_username(message.text.split()[0][1:], session)
                break

            if entity.type == "text_mention":
                user = await Users.get_user(entity.user.id, session)
                break

    if user is None:
        user = await Users.get_user(message.text, session)
    print(user)
    if user is None:
        text = texts.error_input_user
        builder.button(text=texts.back_button, callback_data="admin")
        return await message.answer(text, reply_markup=builder.as_markup())

    text = ''
    await state.update_data(user_id=user.user_id)
    current_state = await state.get_state()
    print(current_state)
    if current_state == UpdateUser.add_admin.state:
        print(current_state)
        text = f"Админ панель выдана {user.name}:{user.user_id}"
        builder.button(text=texts.back_button, callback_data="admin")
        await Users.update_user(user.user_id, session, is_admin=True)

    elif current_state == UpdateUser.give_premium.state:
        text = f"Пользователь: {user.name}:{user.user_id} \n{texts.give_premium}"
        tariffs = await Tariffs.get_tariffs(session)
        for tariff in tariffs:
            builder.button(text=tariff.name, callback_data=TariffCallbackFactory(id=tariff.id, action="give"))

    elif current_state == UpdateUser.clear_reviews.state:
        text = f"{texts.confirmation_clean_reviews} {user.name}:{user.user_id}"
        builder.button(text="Да", callback_data="success_clear")
        builder.button(text="Нет", callback_data="admin")

    elif current_state == UpdateUser.block.state:
        text = f"{texts.confirmation_block} {user.name}:{user.user_id}"
        builder.button(text="Да", callback_data="success_block")
        builder.button(text="Нет", callback_data="admin")

    await message.answer(text, reply_markup=builder.as_markup())


@router.callback_query(F.data == 'success_clear')
async def success_clear(callback: types.CallbackQuery, state: FSMContext, session):
    state_data = await state.get_data()
    await Reviews.clear_user_reviews(state_data.get('user_id'), session)
    text = "Очищено"
    builder = InlineKeyboardBuilder()
    builder.button(text="Назад", callback_data="admin")
    await callback.message.edit_text(text, reply_markup=builder.as_markup())


@router.callback_query(F.data == 'success_block')
async def success_clear(callback: types.CallbackQuery, state: FSMContext, session):
    state_data = await state.get_data()
    await Users.update_user(state_data.get('user_id'), session, is_blocked=True)
    text = "Заблокирован"
    builder = InlineKeyboardBuilder()
    builder.button(text="Назад", callback_data="admin")
    await callback.message.edit_text(text, reply_markup=builder.as_markup())


@router.callback_query(TariffCallbackFactory.filter(F.action == "give"))
async def give_premium(callback: types.CallbackQuery, callback_data: TariffCallbackFactory, state: FSMContext, session):
    state_data = await state.get_data()
    tariff = await Tariffs.get_tariff(callback_data.id, session)
    await Users.update_user(state_data.get('user_id'), session, premium=datetime.timedelta(days=tariff.duration))
    text = f"""{texts.give_premium_success} на {tariff.name}  пользователю c ID {state_data.get('user_id')}"""
    builder = InlineKeyboardBuilder()
    builder.button(text="Назад", callback_data="admin")

    await callback.message.edit_text(text, reply_markup=builder.as_markup())

