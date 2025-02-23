import asyncio
from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ContentType
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters.command import Command
from aiogram.utils.chat_action import ChatActionSender
import re
from db_conf import db

from dotenv import load_dotenv
import os
get = os.getenv

load_dotenv()

bot = Bot(token=get('BOT_TOKEN'))

user_router = Router()

class Form(StatesGroup): 
    file = State()

@user_router.message(Command("register"))
async def register_user(message: types.Message):
    user_id = message.from_user.id
    user_status = "guest"
    username = message.from_user.username or "NoUsername"

    await db.add_user(user_id, user_status, username)
    await message.answer("Вы успешно зарегистрированы!")

@user_router.message(Command("start"))
async def on_start(message: types.Message):
    await message.answer('Привет!')

@user_router.message(Command("download_file"))
async def on_start(message: types.Message, state: FSMContext):
    await message.answer('Внесите файл')
    await state.set_state(Form.file)

@user_router.message(F.content_type.in_([ContentType.PHOTO, ContentType.DOCUMENT, ContentType.AUDIO, ContentType.VIDEO]), Form.file)
async def get_user_file(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if message.document:
        file_id = message.document.file_id
        file_type = "документ"
    elif message.photo:
        file_id = message.photo[-1].file_id
        file_type = "фото"
    elif message.video:
        file_id = message.video.file_id
        file_type = "видео"
    elif message.audio:
        file_id = message.audio.file_id
        file_type = "аудио"
    else:
        await message.answer("Файл не распознан.")
        return
    
    await message.answer(f"Ваш файл успешно загружен!")
    await db.add_file(user_id, file_id)
    await state.clear()

@user_router.message(Command("get_file"))
async def on_start(message: types.Message):
    user_id = message.from_user.id
    file_id = await db.get_file_id(user_id)
    await message.answer(f"Ваш ID файла: {file_id}")