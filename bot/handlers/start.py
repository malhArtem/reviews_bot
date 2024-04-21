from aiogram import Router, types, F
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.handlers.users.pay.crypto_pay import check_user_payments
from bot.handlers.users.profile import profile_panel
from bot.utils.filters import AgreeFilter
from bot.utils.keyboard import ProfileCallbackFactory, ReviewsCallbackFactory, AddReviewCallbackFactory, \
    ComplaintCallbackFactory
from bot.utils.texts import get_profile_text
from db.models.users import Users
from utils.parse_texts import parse_policy, texts

router = Router()
router.message.filter(F.chat.type == "private")
router.callback_query.filter(F.message.chat.type == "private")

class AgreeState(StatesGroup):
    agree = State()
# texts_polit = "Текст о политике бота"


async def check_args(builder, args, message, session):
    if len(args) > 1:
        if args[0] == 'usr':

            user = await Users.get_user(args[1], session)

            if user is None:
                text = texts.error_input_user
                builder.button(text=texts.back_button, callback_data="start")
                return text, builder

            else:
                print(user)
                if user.is_blocked:
                    return "Пользователь заблокирован", builder

                else:
                    builder = profile_panel(builder, user.user_id == str(message.from_user.id), user, message)

                text = await get_profile_text(user, message)
                builder.adjust(2)

        elif args[0] == "invc":
            days = await check_user_payments(str(message.from_user.id), session)
            if days:
                text = texts.success_invoice
            else:
                text = f"Нет новых оплаченных платежей"
            builder.button(text=texts.back_button, callback_data=ProfileCallbackFactory(user_id=str(message.from_user.id)))

        return text, builder
    else:
        return None


@router.message(CommandStart(deep_link=True), AgreeFilter())
async def start(message: types.Message, command: CommandObject, session):
    args = command.args.split(('_'))
    builder = InlineKeyboardBuilder()
    text, builder = await check_args(builder, args, message, session)
    if text is not None:
        await message.answer(text, reply_markup=builder.as_markup)



@router.message(CommandStart(deep_link=True), ~AgreeFilter())
async def start(message: types.Message, command: CommandObject, state: FSMContext, session):
    await state.update_data(deep_link=command.args)
    await state.set_state(AgreeState.agree)
    text_policy = parse_policy()
    text = (f"{texts.start_policy}\n"
            f"{text_policy}")
    builder = InlineKeyboardBuilder()
    builder.button(text=texts.start_policy_button, callback_data="agree")
    await message.answer(text=text, reply_markup=builder.as_markup())


@router.message(CommandStart(), AgreeFilter())
async def start(message: types.Message, session):
    text = texts.start

    builder = InlineKeyboardBuilder()
    builder.button(text=texts.start_button_profile, callback_data=ProfileCallbackFactory(user_id=str(message.from_user.id)))
    builder.button(text=texts.start_button_reviews, callback_data="reviews_about")
    builder.adjust(1)
    await message.answer(text, reply_markup=builder.as_markup())


@router.message(CommandStart())
async def start(message: types.Message, session):
    # await Users.add_user(message.from_user.id, message.chat.id, message.from_user.full_name, session)
    text_policy = parse_policy()
    text = (f"{texts.start_policy}\n"
            f"{text_policy}")
    builder = InlineKeyboardBuilder()
    builder.button(text=texts.start_policy_button, callback_data="agree")
    await message.answer(text=text, reply_markup=builder.as_markup())


@router.callback_query(F.data == 'start')
async def start(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()

    text = texts.start

    builder = InlineKeyboardBuilder()
    builder.button(text=texts.start_button_profile,
                   callback_data=ProfileCallbackFactory(user_id=str(callback.from_user.id)))
    builder.button(text=texts.start_button_reviews, callback_data="reviews_about")
    builder.adjust(1)
    await callback.message.edit_text(text, reply_markup=builder.as_markup())


@router.callback_query(F.data == "agree", AgreeState.agree)
async def add_agree(callback: types.CallbackQuery, session, state: FSMContext):
    await Users.update_user(callback.from_user.id, session, agree=True)
    state_data = await state.get_data()
    await state.clear()
    args = state_data.get('deep_link').split(('_'))
    builder = InlineKeyboardBuilder()
    text, builder = await check_args(builder, args, callback, session)

    if text is not None:
        await callback.message.edit_text(text, reply_markup=builder.as_markup())


@router.callback_query(F.data == "agree")
async def add_agree(callback: types.CallbackQuery, session):
    await Users.update_user(callback.from_user.id, session, agree=True)
    text = texts.start

    builder = InlineKeyboardBuilder()
    builder.button(text=texts.start_button_profile,
                   callback_data=ProfileCallbackFactory(user_id=str(callback.from_user.id)))
    builder.button(text=texts.start_button_reviews, callback_data="reviews_about")
    builder.adjust(1)
    await callback.message.edit_text(text, reply_markup=builder.as_markup())


@router.message(Command("id"))
async def get_id(message: types.Message):
    await message.answer(str(message.chat.id))