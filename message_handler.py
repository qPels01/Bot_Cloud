import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.enums.dice_emoji import DiceEmoji
from aiogram.filters.command import Command

class Command_Handler:
    def __init__(self, token: str):
        self.bot = Bot(token=token)
        self.dp = Dispatcher()

        self.register_handlers()

    def register_handlers(self):
        self.dp.message.register(self.start_command, Command(commands=['start']))
        self.dp.message.register(self.echo_message)
    
    async def start_command(self, message: types.Message):
        await message.answer("Привет!")

    async def echo_message(self, message: types.Message):  # Добавил обработчик сообщений
        await message.answer(message.text)

    def get_bot(self):
        return self.bot

    def get_dp(self):
        return self.dp