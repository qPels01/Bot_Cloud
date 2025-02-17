import asyncio
from db_conf import DatabaseManager

from dotenv import load_dotenv
import os
get = os.getenv

load_dotenv()

import asyncio
import logging
from message_handler import Command_Handler

bot_handler = Command_Handler(token=get("BOT_TOKEN"))   
PG_LINK=f"postgresql://{get("DB_USER")}:{get("DB_PASSWORD")}@{get("DB_HOST")}:5432/{get("DB_NAME")}"

db = DatabaseManager(PG_LINK)

async def main():
    await db.connect()
    dp = bot_handler.get_dp()
    bot = bot_handler.get_bot()
    try:
        await dp.start_polling(bot)
    finally:
        await db.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO) 
    asyncio.run(main())