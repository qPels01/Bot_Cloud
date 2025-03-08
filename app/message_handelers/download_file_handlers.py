import app.keyboards as kb
from aiogram import Bot, types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InputMediaPhoto, InputMediaVideo
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters.command import Command
from db_conf import db


from dotenv import load_dotenv
import os
get = os.getenv

load_dotenv()

bot = Bot(token=get('BOT_TOKEN'))

download_file_router = Router()

class Form(StatesGroup):
    folders = State()

@download_file_router.message(Command("send_file"))
async def get_file(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    folder_name = await db.get_folders_by_id(user_id)

    await message.answer(f"Выберите папку:", reply_markup= await kb.available_folders(folder_name))
    await state.update_data(user_id=user_id)
    await state.set_state(Form.folders)

@download_file_router.callback_query(Form.folders, F.data.startswith("folder_"))
async def file_id(callback: CallbackQuery, state: FSMContext):
    folder_name = callback.data.split("_", 1)[1]
    data = await state.get_data()
    user_id = data.get("user_id")

    files = await db.get_file(user_id, folder_name)
    if not files:
        await callback.message.answer("❗ В этой папке нет файлов.")
        return
    
    media = []
    other_media = []

    for file in files[:10]:
        file_id, file_type = file
        if file_type == "фото":
            media.append(InputMediaPhoto(media=file_id))
        elif file_type == "видео":
            media.append(InputMediaVideo(media=file_id))
        elif file_type in ["документ", "аудио"]:
            other_media.append((file_id, file_type))

    if media:
        await callback.message.answer_media_group(media=media)

    for file_id, file_type in other_media:
        if file_type == "документ":
            await callback.message.answer_document(document=file_id)
        elif file_type == "аудио":
            await callback.message.answer_audio(audio=file_id)

    await state.clear()