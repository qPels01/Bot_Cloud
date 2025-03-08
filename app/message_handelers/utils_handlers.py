import app.keyboards as kb
from aiogram import Bot, types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ContentType, ReplyKeyboardRemove, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters.command import Command, CommandStart
from db_conf import db
from sqlalchemy.exc import IntegrityError
from asyncpg.exceptions import UniqueViolationError

from dotenv import load_dotenv
import os
get = os.getenv

load_dotenv()

bot = Bot(token=get('BOT_TOKEN'))

user_router = Router()

class Form(StatesGroup): 
    folder = State()

@user_router.message(CommandStart())
async def on_start(message: types.Message):
    await message.answer('Привет! Чтобы пользоваться ботом, тебе нужно сначала зарегистрироваться.', 
                        reply_markup=kb.start_kb)

@user_router.message(F.text == "Зарегистрироваться")
async def register_user(message: types.Message):
    user_id = message.from_user.id
    user_status = "guest"
    username = message.from_user.username or "NoUsername"

    is_registered = await db.is_user_registered(user_id)

    await message.delete()

    if is_registered:
        await message.answer("Вы уже зарегистрированы! ✅", reply_markup=ReplyKeyboardRemove())
    else:
        await db.add_user(user_id, user_status, username)
        await message.answer("Вы успешно зарегистрированы! 🎉", reply_markup=ReplyKeyboardRemove())

@user_router.message(Command("delete_folder"))
async def delete_file(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    selected_folder = await db.get_folders_by_id(user_id)

    await message.answer(f"Выберите папку:", reply_markup= await kb.available_folders(selected_folder))
    await state.update_data(user_id=user_id)
    await state.set_state(Form.folder)

@user_router.callback_query(Form.folder, F.data.startswith("folder_"))
async def file_id(callback: CallbackQuery, state: FSMContext):
    selected_folder = callback.data.split("_", 1)[1]
    data = await state.get_data()
    user_id = data.get("user_id")

    await db.delete_folder(user_id, selected_folder)
    await callback.message.answer(f"Папка <b>{selected_folder}</b> успешно удалена!", parse_mode="HTML")

    await state.clear()