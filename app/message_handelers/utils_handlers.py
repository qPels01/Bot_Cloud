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
    selected_folder = State()
    renamed_folder = State()

@user_router.message(CommandStart())
async def on_start(message: types.Message):
    await message.answer('Привет! Чтобы пользоваться ботом, тебе нужно сначала зарегистрироваться.', 
                        reply_markup=kb.start_kb)

@user_router.message(F.text == "Зарегистрироваться")
async def register_user(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username or "NoUsername"

    is_registered = await db.is_user_registered(user_id)

    await message.delete()

    if is_registered:
        await message.answer("Вы уже зарегистрированы! ✅", reply_markup=ReplyKeyboardRemove())
    else:
        await db.add_user(user_id, username)
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

@user_router.message(Command("rename_folder"))
async def choose_folder_to_rename(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    await state.update_data(user_id=user_id)

    choosed_folder = await db.get_folders_by_id(user_id)

    await message.answer(f"Выберите папку которую хотите переименовать:", reply_markup= await kb.available_folders(choosed_folder))
    await state.update_data(user_id=user_id)
    await state.set_state(Form.selected_folder)

@user_router.callback_query(Form.selected_folder, F.data.startswith("folder_"))
async def folder_id(callback: CallbackQuery, state: FSMContext):
    folder = callback.data.split("_", 1)[1]
    await state.update_data(folder=folder)

    await callback.message.answer("Введите новое название папки")
    await state.set_state(Form.renamed_folder)

@user_router.message(Form.renamed_folder)
async def rename_folder(message: types.Message, state: FSMContext):
    new_foldername = message.text

    data = await state.get_data()
    user_id = data.get("user_id")
    folder = data.get("folder")

    await db.rename_folder(user_id, folder, new_foldername)
    await message.answer(f"Папка <b>{folder}</b> переименованна в папку <b>{new_foldername}</b>!", parse_mode="HTML")

    await state.clear()