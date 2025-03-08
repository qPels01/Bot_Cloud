import hashlib
import aiohttp
from aiogram import Bot

from dotenv import load_dotenv
import os
get = os.getenv

load_dotenv()

bot = Bot(token=get('BOT_TOKEN'))

async def get_file_hash_from_telegram(file_id: str) -> str:
    file = await bot.get_file(file_id)
    file_path = file.file_path
    file_url = f"https://api.telegram.org/file/bot{bot.token}/{file_path}"

    hasher = hashlib.sha256()
    
    async with aiohttp.ClientSession() as session:
        async with session.get(file_url) as response:
            while chunk := await response.content.read(4096):
                hasher.update(chunk)
    
    return hasher.hexdigest()