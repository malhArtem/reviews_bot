from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.handlers.users.profile import profile_panel
from bot.utils.keyboard import ReviewsCallbackFactory, AddReviewCallbackFactory, ComplaintCallbackFactory
from bot.utils.texts import get_profile_text
from db.models.users import Users
from utils.parse_texts import texts

router = Router()
router.message.filter(F.chat.type == "private")
router.callback_query.filter(F.message.chat.type == "private")


class SearchState(StatesGroup):
    input = State()

@router.callback_query(F.data == "reviews_about")
async def reviews_about(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    text = texts.input_user_text
    builder = InlineKeyboardBuilder()

    builder.button(text=texts.back_button, callback_data="start")

    await state.set_state(SearchState.input)
    await callback.message.edit_text(text, reply_markup=builder.as_markup())


@router.message(F.text, SearchState.input)
async def search(message: types.Message, state: FSMContext, session):
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

    if user is None:
        text = texts.error_input_user
        builder.button(text=texts.back_button, callback_data="start")
        return await message.answer(text, reply_markup=builder.as_markup())

    else:
        text = await get_profile_text(user, message)
        builder = profile_panel(builder, user.user_id == str(message.from_user.id),user, message)

        await message.answer(text, reply_markup=builder.as_markup())
