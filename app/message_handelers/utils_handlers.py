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
    file = State()
    filename = State()
    create_new_folder = State()
    choose_folder = State()
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


