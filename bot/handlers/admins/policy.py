from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.utils.filters import AdminFilter
from utils.parse_texts import edit_policy, texts

router = Router()
router.message.filter(F.chat.type == "private")
router.callback_query.filter(F.message.chat.type == "private")

router.callback_query.filter(AdminFilter())
router.message.filter(AdminFilter())

class PolicyStates(StatesGroup):
    input = State()


@router.callback_query(F.data == "policy")
async def policy(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    text = texts.start_policy
    builder = InlineKeyboardBuilder()
    builder.button(text="Назад", callback_data="admin")
    await state.set_state(PolicyStates.input)
    await callback.message.edit_text(text, reply_markup=builder.as_markup())

@router.message(PolicyStates.input, F.text)
async def policy(message: types.Message, state: FSMContext):
    policy_text = message.html_text
    await state.clear()
    text = "Изменено"
    builder = InlineKeyboardBuilder()
    builder.button(text=texts.back_button, callback_data="admin")
    edit_policy(policy_text)
    await message.answer(text, reply_markup=builder.as_markup())