from aiogram import Router, types, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.utils.filters import AgreeFilter, PremiumFilter
from bot.utils.texts import get_profile_text
from db.models.reviews import Reviews
from db.models.users import Users

from bot.utils.keyboard import ReviewsCallbackFactory, ProfileCallbackFactory, AddReviewCallbackFactory, \
    ComplaintCallbackFactory
from utils.parse_texts import texts

router = Router()
router.message.filter(F.chat.type == "private")
router.callback_query.filter(F.message.chat.type == "private")

router.message.filter(AgreeFilter())
router.callback_query.filter(AgreeFilter())


class AboutState(StatesGroup):
    input_about = State()


def profile_panel(builder, flag: bool, profile, callback):
    if flag:
        builder.button(text=texts.my_profile_buy, callback_data="premium")
        builder.button(text=texts.my_profile_reviews, callback_data=ReviewsCallbackFactory(user_id=str(callback.from_user.id)))
        builder.button(text=texts.my_profile_about_me, callback_data="about_my")
        builder.button(text=texts.back_button, callback_data="start")
    else:
        builder.button(text=texts.user_profile_reviews, callback_data=ReviewsCallbackFactory(user_id=str(profile.user_id)))
        builder.button(text=texts.user_profile_add_reviews, callback_data=AddReviewCallbackFactory(about_user_id=str(profile.user_id)))
        builder.button(text=texts.user_profile_complain, callback_data=ComplaintCallbackFactory(about=str(profile.user_id)))
        builder.button(text=texts.back_button, callback_data="start")
    builder.adjust(2)
    return builder


@router.callback_query(ProfileCallbackFactory.filter())
async def profile_handler(callback: types.CallbackQuery, callback_data: ProfileCallbackFactory, session, state: FSMContext):
    await state.clear()
    profile = await Users.get_user(callback_data.user_id, session)
    builder = InlineKeyboardBuilder()
    builder = profile_panel(builder, callback_data.user_id == str(callback.from_user.id), profile, callback)

    text = await get_profile_text(profile, callback)

    await callback.answer()
    await callback.message.edit_text(text=text, reply_markup=builder.as_markup())


@router.callback_query(ReviewsCallbackFactory.filter())
async def get_reviews(callback: types.CallbackQuery, callback_data: ReviewsCallbackFactory, session):
    builder = InlineKeyboardBuilder()
    limit = 3
    reviews, pages = await Users.get_user_reviews(callback_data.user_id, session, offset=callback_data.page)
    if len(reviews) == 0:
        return await callback.answer("Нет отзывов")
    count_reviews = len(reviews)
    text = ''

    for review in reviews[:limit]:
        text += f"<a href='t.me/{(await callback.bot.me()).username}?start=usr_{review.reviewer.user_id}'>{review.reviewer.name}</a>"
        text += f" (@{review.reviewer.username}):\n" if review.reviewer.username is not None else ":\n"
        text += (f"Оценка: {review.evaluation}\n"
                 f"Отзыв: {review.text}\n\n")


    if callback_data.page > 0:
        builder.button(text="<", callback_data=ReviewsCallbackFactory(user_id=callback_data.user_id, page=callback_data.page-limit))

    builder.button(text=f"{callback_data.page//limit + 1}/{pages}", callback_data="pass")

    if count_reviews > limit:
        builder.button(text=">",
                       callback_data=ReviewsCallbackFactory(user_id=callback_data.user_id, page=callback_data.page + limit))

    builder.row(InlineKeyboardButton(text=texts.back_button, callback_data=ProfileCallbackFactory(user_id=str(callback_data.user_id)).pack()))

    await callback.message.edit_text(text, reply_markup=builder.as_markup())


@router.callback_query(F.data == "about_my", PremiumFilter())
async def about_my(callback: types.CallbackQuery, state: FSMContext):
    text = texts.about_me
    builder = InlineKeyboardBuilder()
    builder.button(text=texts.back_button, callback_data=ProfileCallbackFactory(user_id=str(callback.from_user.id)))

    await state.set_state(AboutState.input_about)

    await callback.message.edit_text(text, reply_markup=builder.as_markup())


@router.callback_query(F.data == "about_my")
async def about_my(callback: types.CallbackQuery):
    text = texts.about_me_premium
    builder = InlineKeyboardBuilder()
    builder.button(text=texts.about_me_premium_button, callback_data="premium")
    builder.button(text=texts.back_button, callback_data=ProfileCallbackFactory(user_id=str(callback.from_user.id)))
    await callback.message.edit_text(text, reply_markup=builder.as_markup())



@router.message(F.text, AboutState.input_about)
async def input_about(message: types.Message, state: FSMContext, session):
    if len(message.text) > 300:
        text = texts.error_long_about_me
    else:
        await Users.update_user(message.from_user.id, session, about=message.html_text)
        await state.clear()
        text = texts.success_about_me
    builder = InlineKeyboardBuilder()
    builder.button(text=texts.back_button, callback_data=ProfileCallbackFactory(user_id=str(message.from_user.id)))
    await message.answer(text, reply_markup=builder.as_markup())
