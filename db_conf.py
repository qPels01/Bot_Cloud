import asyncpg
import logging

class DatabaseManager:
    def __init__(self, dsn: str):
        self.dsn = dsn
        self.pool = None  

    async def connect(self):
        try:
            self.pool = await asyncpg.create_pool(dsn=self.dsn)
            logging.info("✅ Подключение к базе данных успешно!")
        except Exception as e:
            logging.error(f"❌ Ошибка подключения к БД: {e}")

    async def close(self):
        if self.pool:
            await self.pool.close()
            logging.info("🔌 Соединение с БД закрыто")

