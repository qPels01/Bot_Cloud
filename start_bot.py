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
import app.message_handelers.utils_handlers as handler_utils
import app.message_handelers.upload_file_handlers as handler_upload
import app.message_handelers.download_file_handlers as handler_download

bot = Bot(token=get('BOT_TOKEN'))
PG_LINK=f"postgresql://{get("DB_USER")}:{get("DB_PASSWORD")}@{get("DB_HOST")}:5432/{get("DB_NAME")}"

async def set_commands():
    commands = [BotCommand(command='start', description='Старт'),
                BotCommand(command='upload_file', description='Загрузить файл в бота'),
                BotCommand(command='send_file', description='Получить файлы'),
                BotCommand(command='delete_folder', description='Удалить папку')]
    await bot.set_my_commands(commands, BotCommandScopeDefault())

async def main():
    await db.connect()
    await set_commands()
    dp = Dispatcher()

    dp.include_routers(handler_utils.user_router, handler_upload.upload_file_router, handler_download.download_file_router)
    try:
        await dp.start_polling(bot)
    finally:
        await db.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO) 
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")