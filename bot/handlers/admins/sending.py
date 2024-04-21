import asyncio

from aiogram import Router, types, F
from aiogram.exceptions import TelegramRetryAfter, TelegramForbiddenError
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.utils.filters import AdminFilter
from bot.utils.logger import logger
from db.models.advertisements import Advertisements
from db.models.users import Users
from utils.parse_texts import texts


async def all_sending(session, bot, text=None,  photo=None, button: str = None):
    users = await Users.get_users(session)
    builder = InlineKeyboardBuilder()
    if button is not None:
        button = button.split('+')
    if button is not None:
        builder.button(text=f"{button[0]}", url=f"{button[1]}")

    for user in users:
        print(user)
        try:
            if photo is not None:
                await bot.send_photo(user, photo=photo, caption=text, reply_markup=builder.as_markup())
            else:
                await bot.send_message(user, text, reply_markup=builder.as_markup())
            await asyncio.sleep(0.2)

        except TelegramRetryAfter:
            await asyncio.sleep(1)

            if photo is not None:
                await bot.send_photo(user, photo=photo, caption=text, reply_markup=builder.as_markup())
            else:
                await bot.send_message(user, text, reply_markup=builder.as_markup())

        except TelegramForbiddenError:
            pass

        except Exception as e:
            logger.error(e)


router = Router()
router.message.filter(F.chat.type == "private")
router.callback_query.filter(F.message.chat.type == "private")
router.callback_query.filter(AdminFilter())
router.message.filter(AdminFilter())


def sender_panel(builder):
    text = texts.sender_link_input

    builder.button(text="не надо", callback_data="pass_link")
    builder.button(text="Назад", callback_data="sending")
    builder.button(text="Отмена", callback_data="admin")
    return builder, text

class SendingStates(StatesGroup):
    input_text = State()
    input_button = State()


@router.callback_query(F.data == 'sending')
async def sending(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    text = texts.sender_text_input
    builder = InlineKeyboardBuilder()
    builder.button(text=texts.back_button, callback_data="admin")

    await state.set_state(SendingStates.input_text)
    await callback.message.edit_text(text, reply_markup=builder.as_markup())


@router.message(F.photo, SendingStates.input_text)
@router.message(F.text, SendingStates.input_text)
async def sending(message: types.Message, state: FSMContext):
    if message.photo:
        await state.update_data(text=message.html_text)
        await state.update_data(photo=message.photo[-1].file_id)
    else:
        await state.update_data(text=message.html_text)

    await state.set_state(SendingStates.input_button)


    builder = InlineKeyboardBuilder()
    builder, text = sender_panel(builder)

    await message.answer(text, reply_markup=builder.as_markup())


@router.message(F.text, SendingStates.input_button)
async def sending(message: types.Message, state: FSMContext):
    flag = False
    url = ''
    builder = InlineKeyboardBuilder()
    for entity in message.entities:
        if entity.type == 'url':
            flag = True
            url = message.text[entity.offset:entity.offset + entity.length]
            print(url)
            break
    button = message.text.split('+')
    if len(button) != 2 or button[1] != url or not flag:
        builder, text2 = sender_panel(builder)
        return await message.answer("Неверный формат, попробуйте еще раз", reply_markup=builder.as_markup())

    await state.update_data(button=message.text)
    state_data = await state.get_data()
    builder.button(text=button[0], url=button[1])
    builder.button(text="Подтвердить", callback_data="success_sending")
    builder.button(text=texts.back_button, callback_data="input_link")
    builder.button(text="Отмена", callback_data="admin")

    builder.adjust(1, 3)

    if state_data.get("photo") is not None:
        await message.answer_photo(state_data.get("photo"), caption=state_data.get("text"), reply_markup=builder.as_markup())
    else:
        await message.answer(state_data.get("text"), reply_markup=builder.as_markup())


@router.callback_query(F.data == "input_link", StateFilter(SendingStates))
async def sending(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(SendingStates.input_button)
    builder = InlineKeyboardBuilder()
    builder, text = sender_panel(builder)

    if callback.message.photo:
        await callback.message.answer(text, reply_markup=builder.as_markup())
        await callback.message.delete()
    else:
        await callback.message.edit_text(text, reply_markup=builder.as_markup())


@router.callback_query(F.data == "pass_link")
async def sending(callback: types.CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    builder = InlineKeyboardBuilder()
    builder.button(text="Подтвердить", callback_data="success_sending")
    builder.button(text=texts.back_button, callback_data="input_link")
    builder.button(text="Отмена", callback_data="admin")

    builder.adjust(1, 3)

    await callback.answer()
    if state_data.get("photo") is not None:
        await callback.message.answer_photo(state_data.get("photo"), caption=state_data.get("text"),
                                   reply_markup=builder.as_markup())
        await callback.message.delete()
    else:
        await callback.message.edit_text(state_data.get("text"), reply_markup=builder.as_markup())


@router.callback_query(F.data == "success_sending")
async def sending(callback: types.CallbackQuery, state: FSMContext, session):
    state_data = await state.get_data()
    await state.clear()
    builder = InlineKeyboardBuilder()
    builder.button(text=texts.back_button, callback_data="admin")
    await Advertisements.add_advertisements(session, **state_data)
    await callback.answer()
    if callback.message.photo is not None:
        await callback.message.answer(texts.sender_begin, reply_markup=builder.as_markup())
        await callback.message.delete()
    else:
        await callback.message.edit_text(texts.sender_begin, reply_markup=builder.as_markup())
    await asyncio.create_task(all_sending(session, callback.bot, **state_data))
