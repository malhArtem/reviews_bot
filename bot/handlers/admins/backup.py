import asyncio
import datetime

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InputFile, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.utils.filters import AdminFilter
from utils.db_dump import create_dump_postgres, restore_dump_postgres
from utils.parse_texts import texts

router = Router()
router.callback_query.filter(AdminFilter())
router.message.filter(AdminFilter())


class BackupStates(StatesGroup):
    input = State()

@router.callback_query(F.data == "backup")
async def backup(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    builder = InlineKeyboardBuilder()
    builder.button(text="Экспортировать", callback_data='export_db')
    builder.button(text="Импортировать", callback_data='import_db')
    builder.button(text=texts.back_button, callback_data='admin')
    builder.adjust(2, 1)
    await callback.message.edit_text("Выберите  экспортировать или импортировать базу данных", reply_markup=builder.as_markup())


@router.callback_query(F.data == "export_db")
async def export_db(callback: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.button(text=texts.back_button, callback_data="admin_new")
    dump = create_dump_postgres(datetime.datetime.utcnow())
    print(dump)
    if dump:
        dump_file = FSInputFile(dump)
        await callback.bot.send_document(callback.message.chat.id, dump_file)
    await callback.message.edit_text("Бекап создан", reply_markup=builder.as_markup())


@router.callback_query(F.data == 'import_db')
async def import_db(callback: types.CallbackQuery, state: FSMContext):
    builder = InlineKeyboardBuilder()
    builder.button(text=texts.back_button, callback_data='backup')
    await state.set_state(BackupStates.input)
    await callback.message.edit_text("Загрузите файл дампа", reply_markup=builder.as_markup())


@router.message(F.document, BackupStates.input)
async def import_db(message: types.Message, state: FSMContext):
    now = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
    file = await message.bot.get_file(message.document.file_id)
    await message.bot.download_file(file.file_path, destination=f"dumps/download/{now}")
    dump = restore_dump_postgres(f"dumps/download/{now}")
    text = "Бекап загружен" if dump else "Ошибка бекапа"
    builder = InlineKeyboardBuilder()
    builder.button(text=texts.back_button, callback_data='admin')
    await message.answer(text, reply_markup=builder.as_markup())