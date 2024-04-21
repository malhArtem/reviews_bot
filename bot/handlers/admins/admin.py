import datetime

from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.utils.filters import AdminFilter
from db.models.statistics_query import Statistics
from utils.db_dump import create_dump_postgres
from utils.parse_texts import texts

router = Router()
router.callback_query.filter(AdminFilter())
router.message.filter(AdminFilter())
router.message.filter(F.chat.type == "private")
router.callback_query.filter(F.message.chat.type == "private")

def admin_panel():
    builder = InlineKeyboardBuilder()
    builder.button(text="Статистика", callback_data="stat")
    builder.button(text="Рассылка", callback_data="sending")
    builder.button(text="Цены", callback_data="prices")
    builder.button(text="Выдать админку", callback_data="add_admin")
    builder.button(text="Политика бота", callback_data="policy")
    builder.button(text="Выдать премиум", callback_data="give_premium")
    builder.button(text="Очистка отзывов", callback_data="clear_reviews")
    builder.button(text="Заблокировать", callback_data="block")
    builder.button(text="Бекап БД", callback_data="backup")
    builder.adjust(3)

    text = texts.admin

    return builder, text
@router.message(Command("admin"))
async def admin(message: types.Message, state: FSMContext):
    await state.clear()
    builder, text = admin_panel()

    await message.answer(text, reply_markup=builder.as_markup())


@router.callback_query(F.data == "admin")
async def admin(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    builder, text = admin_panel()

    if callback.message.photo is not None:
        await callback.message.answer(text, reply_markup=builder.as_markup())
        await callback.message.delete()
    else:
        await callback.message.edit_text(text, reply_markup=builder.as_markup())


@router.callback_query(F.data == "admin_new")
async def admin(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    builder, text = admin_panel()

    await callback.answer()
    try:
        await callback.message.delete()
    except Exception as e:
        pass
    await callback.message.answer(text, reply_markup=builder.as_markup())


@router.callback_query(F.data == "stat")
async def statistics(callback: types.CallbackQuery, session):
    statistic = await Statistics.get_stats(session)
    text = (f"<u>Статистика</u>:\n\n"
            f"Кол-во пользователей: {statistic[0]}\n"
            f"Кол-во премиум ползьователей: {statistic[1]}\n"
            f"Кол-во рекламных сообщений: {statistic[2]}\n"
            f"Всего отзывов: {statistic[3]}")

    builder = InlineKeyboardBuilder()
    builder.button(text="Обновить", callback_data="stat")
    builder.button(text=texts.back_button, callback_data="admin")
    await callback.answer()
    try:
        await callback.message.edit_text(text, reply_markup=builder.as_markup())
    except Exception as e:
        print(e)





