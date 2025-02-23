import asyncio
from db_conf import DatabaseManager
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand, BotCommandScopeDefault
from db_conf import db

from dotenv import load_dotenv
import os
get = os.getenv

load_dotenv()

import asyncio
import logging
import message_handler

bot = Bot(token=get('BOT_TOKEN'))
PG_LINK=f"postgresql://{get("DB_USER")}:{get("DB_PASSWORD")}@{get("DB_HOST")}:5432/{get("DB_NAME")}"

async def set_commands():
    commands = [BotCommand(command='start', description='Старт'),
                BotCommand(command='download_file', description='Загрузить файл'),
                BotCommand(command='register', description='Регистрация'),
                BotCommand(command='get_file', description='Получить ID файла'),]
    await bot.set_my_commands(commands, BotCommandScopeDefault())

async def main():
    await db.connect()
    await set_commands()
    dp = Dispatcher()

    dp.include_router(message_handler.user_router)
    try:
        await dp.start_polling(bot)
    finally:
        await db.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO) 
    asyncio.run(main())