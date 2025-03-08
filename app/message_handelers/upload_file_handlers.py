import app.keyboards as kb
from aiogram import Bot, types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ContentType, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters.command import Command
from db_conf import db
from sqlalchemy.exc import IntegrityError
from asyncpg.exceptions import UniqueViolationError
from middlewares import get_file_hash_from_telegram

from dotenv import load_dotenv
import os
get = os.getenv

load_dotenv()

bot = Bot(token=get('BOT_TOKEN'))

upload_file_router = Router()

class Form(StatesGroup): 
    file = State()
    filename = State()
    create_new_folder = State()
    choose_folder = State()
    folder = State()


@upload_file_router.message(Command("upload_file"))
async def on_start(message: types.Message, state: FSMContext):
    await message.answer('Внесите файл')
    await state.set_state(Form.file)

@upload_file_router.message(F.content_type.in_([ContentType.PHOTO, ContentType.DOCUMENT, ContentType.AUDIO, ContentType.VIDEO]), Form.file)
async def get_user_file(message: Message, state: FSMContext):

    if message.document:
        file_id = message.document.file_id
        file_type = "документ"
        await state.update_data(file_id=file_id, file_type=file_type)
    elif message.photo:
        file_id = message.photo[-1].file_id
        file_type = "фото"
        await state.update_data(file_id=file_id, file_type=file_type)
    elif message.video:
        file_id = message.video.file_id
        file_type = "видео"
        await state.update_data(file_id=file_id, file_type=file_type)
    elif message.audio:
        file_id = message.audio.file_id
        file_type = "аудио"
        await state.update_data(file_id=file_id, file_type=file_type)
    else:
        await message.answer("❗ Ошибка: файл не распознан.")
        return

    await message.answer("Выбирите действие:", reply_markup= kb.folders_choice)
    await state.set_state(Form.folder)

@upload_file_router.callback_query(F.data == "create_folder")
async def callback_create_folder(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите название новой папки:")
    await state.set_state(Form.create_new_folder)

@upload_file_router.message(Form.create_new_folder)
async def create_folder(message: Message, state: FSMContext):
    user_id = message.from_user.id
    foldername = message.text 

    await db.create_new_folder(user_id, foldername)
    await state.update_data(selected_folder=foldername)
    
    await message.answer(f"✅ Папка <b>{foldername}</b> успешно создана!", parse_mode="HTML")

    folders = await db.get_folders_by_id(user_id)
    
    if folders:
        await message.answer("Выберите папку:", reply_markup= await kb.available_folders(folders))
        await state.set_state(Form.choose_folder)
    else:
        await message.answer("❗ Ошибка: не удалось загрузить список папок.")

@upload_file_router.callback_query(F.data == "choose_folder")
async def callback_folders(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    folders = await db.get_folders_by_id(user_id)

    if not folders:
        await callback.message.answer("У вас нет доступных папок. Создайте новую!")
        return

    await callback.message.answer("Выберите папку📂:", reply_markup= await kb.available_folders(folders))
    await callback.answer()

    await state.set_state(Form.choose_folder)

@upload_file_router.callback_query(F.data.startswith("folder_"), Form.choose_folder)
async def folder_selected(callback: CallbackQuery, state: FSMContext):
    folder_name = callback.data.split("_", 1)[1]  # Извлекаем имя папки из callback_data

    await state.update_data(selected_folder=folder_name)

    await callback.message.answer(f"Вы выбрали папку: <b>{folder_name}</b>", parse_mode="HTML")

    data = await state.get_data()
    user_id = callback.from_user.id
    file_id = data.get("file_id")
    folder = data.get("selected_folder")
    file_type = data.get("file_type")

    file_hash = await get_file_hash_from_telegram(file_id)

    if not file_id:
        await callback.message.answer("❗ Ошибка: файл или имя файла не были переданы.")
        await state.set_state(Form.file)
        return

    existing_folder = await db.unique_error_handler(user_id, file_hash)

    try:
        if file_id:
            await db.add_file(user_id, file_id, folder, file_hash, file_type)
            await callback.message.answer(f"📂 Файл успешно добавлен в папку <b>{folder}</b>!", parse_mode="HTML")
            await state.clear()
        else:
            await state.set_state(Form.file)
    except IntegrityError as e:
        if isinstance(e.orig, UniqueViolationError):
            await callback.message.answer("❗ Файл с таким ID уже существует в базе данных!")
        else:
            await callback.message.answer(f"❗ Этот файл уже добавлен в папку <b>{existing_folder}</b>.",parse_mode="HTML")
        await state.clear()

    except Exception as e:
        await callback.message.answer(f"❗ Произошла непредвиденная ошибка: {str(e)}")
        await state.clear()