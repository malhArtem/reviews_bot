from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.utils.keyboard import AddReviewCallbackFactory, EvaluationReviewCallbackFactory, ProfileCallbackFactory
from db.models.reviews import Reviews
from db.models.users import Users
from utils.parse_texts import texts

router = Router()
router.message.filter(F.chat.type == "private")
router.callback_query.filter(F.message.chat.type == "private")


class AddReviewState(StatesGroup):
    input = State()




@router.callback_query(AddReviewCallbackFactory.filter())
async def add_review(callback: types.CallbackQuery, callback_data: AddReviewCallbackFactory, state: FSMContext, session):
    builder = InlineKeyboardBuilder()
    user = await Users.get_user(callback.from_user.id, session)
    review = await Reviews.get_review_about(callback.from_user.id,callback_data.about_user_id, session)
    if review is not None:
        text = "Вы уже оставили отзыв этому пользователю"
        return await callback.answer(text, show_alert=True)
    reviews = await Reviews.get_today_user_reviews(callback.from_user.id, session)
    if (user.premium and reviews >= 10) or (not user.premium and reviews >= 5):
        text = "Сегодня вы больше не можете оставлять отзывы"
        builder.button(text="Назад", callback_data=ProfileCallbackFactory(user_id=callback_data.about_user_id))
        return await callback.message.edit_text(text, reply_markup=builder.as_markup())

    await state.update_data(about_user=callback_data.about_user_id)
    text = "Поставьте оценку пользователю"

    for i in range(1, 6):
        builder.button(text=str(i), callback_data=EvaluationReviewCallbackFactory(evaluation=i))
    builder.button(text="Назад", callback_data=ProfileCallbackFactory(user_id=callback_data.about_user_id))
    builder.adjust(5, 1)
    await callback.answer()
    await callback.message.edit_text(text, reply_markup=builder.as_markup())


@router.callback_query(EvaluationReviewCallbackFactory.filter())
async def add_review(callback: types.CallbackQuery, callback_data: EvaluationReviewCallbackFactory, state: FSMContext, session):
    await state.update_data(evaluation=callback_data.evaluation)
    await state.set_state(AddReviewState.input)
    state_data = await state.get_data()
    text = "Введите отзыв"
    builder = InlineKeyboardBuilder()
    builder.button(text="назад", callback_data=AddReviewCallbackFactory(about_user_id=state_data.get('about_user')))
    builder.button(text="отмена", callback_data=ProfileCallbackFactory(user_id=state_data.get('about_user')))

    await callback.answer()
    await callback.message.edit_text(text, reply_markup=builder.as_markup())


@router.message(F.text, AddReviewState.input)
async def add_review(message: types.Message, state: FSMContext):
    builder = InlineKeyboardBuilder()
    state_data = await state.get_data()
    if len(message.text) > 150:
        text = "Слишком длинный отзыв, попробуйте снова"
        builder.button(text=texts.back_button, callback_data=AddReviewCallbackFactory(about_user_id=state_data.get('about_user')))
        builder.button(text="Отмена", callback_data=ProfileCallbackFactory(user_id=state_data.get('about_user')))
        return await message.answer(text, reply_markup=builder.as_markup())

    review_text = message.html_text
    text = (f"Оценка: {state_data.get('evaluation')}\n"
            f"Отзыв: {review_text}")

    await state.update_data(review_text=review_text)

    builder.button(text="Подтвердить", callback_data='successful_add_review')
    builder.button(text=texts.back_button, callback_data=EvaluationReviewCallbackFactory(evaluation=state_data.get('evaluation')))
    builder.button(text="Отмена", callback_data=ProfileCallbackFactory(user_id=state_data.get('about_user')))

    await message.answer(text, reply_markup=builder.as_markup())


@router.callback_query(F.data == 'successful_add_review')
async def add_review(callback: types.CallbackQuery, state: FSMContext, session):
    state_data = await state.get_data()
    await state.clear()
    await Reviews.add_review(callback.from_user.id, **state_data, session=session)
    text = "Отзыв добавлен"
    builder = InlineKeyboardBuilder()
    builder.button(text=texts.back_button, callback_data=ProfileCallbackFactory(user_id=state_data.get('about_user')))
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
