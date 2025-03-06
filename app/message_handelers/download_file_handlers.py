import app.keyboards as kb
from aiogram import Bot, types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ContentType, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters.command import Command
from db_conf import db
from sqlalchemy.exc import IntegrityError
from asyncpg.exceptions import UniqueViolationError

from dotenv import load_dotenv
import os
get = os.getenv

load_dotenv()

bot = Bot(token=get('BOT_TOKEN'))

download_file_router = Router()

@download_file_router.message(Command("get_file"))
async def on_start(message: types.Message):
    user_id = message.from_user.id
    file_id = await db.get_file_id(user_id)
    await message.answer(f"Ваш ID файла: {file_id}")