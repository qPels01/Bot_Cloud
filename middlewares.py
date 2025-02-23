from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ContentType
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters.command import Command
from aiogram.utils.chat_action import ChatActionSender
import re
import asyncio

from dotenv import load_dotenv
import os
get = os.getenv

load_dotenv()

bot = Bot(token=get('BOT_TOKEN'))