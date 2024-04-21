from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.utils.config_reader import config
from bot.utils.keyboard import ComplaintCallbackFactory, ProfileCallbackFactory, AnswerComplaintCallbackFactory
from db.models.users import Users
from utils.parse_texts import texts

router = Router()

class ComplaintStates(StatesGroup):
    input = State()


@router.callback_query(ComplaintCallbackFactory.filter())
async def create_complaint(callback: types.CallbackQuery, callback_data: ComplaintCallbackFactory, state: FSMContext):
    builder = InlineKeyboardBuilder()
    builder.button(text="Назад", callback_data=ProfileCallbackFactory(user_id=str(callback_data.about)))
    await state.set_state(ComplaintStates.input)
    await state.update_data(about=callback_data.about)
    text = texts.complaint_input_text
    await callback.message.edit_text(text, reply_markup=builder.as_markup())


@router.message(ComplaintStates.input)
async def create_complaint(message: types.Message, state: FSMContext, session):
    state_data = await state.get_data()
    about = await Users.get_user(state_data.get('about'), session)

    complaint_text = f"Текст жалобы: {message.html_text}\n\n"
    complaint_text += f"Кто жалуется: {message.from_user.full_name}:{message.from_user.id}"
    complaint_text += f" (@{message.from_user.username})\n" if message.from_user.username is not None else "\n"
    complaint_text += f"На кого: {about.name}:{about.user_id}"
    complaint_text += f" (@{about.username})\n" if about.username is not None else "\n"

    photo = None
    if message.photo is not None:
        photo = message.photo[-1].file_id

    builder = InlineKeyboardBuilder()
    builder.button(text="Принять", callback_data=AnswerComplaintCallbackFactory(answer=True, author=str(message.from_user.id), about=state_data.get('about')))
    builder.button(text="Отклонить", callback_data=AnswerComplaintCallbackFactory(answer=False, author=str(message.from_user.id), about=state_data.get('about')))

    builder2 = InlineKeyboardBuilder()
    builder2.button(text="Назад", callback_data=ProfileCallbackFactory(user_id=state_data.get('about')))
    await message.answer("Жалоба отправлена на рассмотрение", reply_markup=builder2.as_markup())
    try:
        if photo is not None:
            await message.bot.send_photo(chat_id=config.moder_channel_id, photo=photo, caption=complaint_text, reply_markup=builder.as_markup())

        else:
            await message.bot.send_message(chat_id=config.moder_channel_id, text=complaint_text, reply_markup=builder.as_markup())

    except Exception as e:
        print(e)


@router.callback_query(AnswerComplaintCallbackFactory.filter())
async def answer_complaint(callback: types.CallbackQuery, callback_data: AnswerComplaintCallbackFactory, session):
    about = await Users.get_user(callback_data.about, session)
    text = f"Ваша жалоба на {about.name}:{about.user_id}"
    text += f" (@{about.username})\n" if about.username is not None else ""

    if callback_data.answer:
        text += " принята"
        complaint_text = callback.message.html_text + "\n\n" + "Жалоба принята"
    else:
        text = " отклонена"
        complaint_text = callback.message.html_text + "\n\n" + "Жалоба отклонена"

    if callback.message.photo:
        await callback.message.edit_caption(caption=complaint_text)
    else:
        await callback.message.edit_text(text=complaint_text)

    try:
        await callback.bot.send_message(callback_data.author, text=text)
    except Exception as e:
        print(e)

