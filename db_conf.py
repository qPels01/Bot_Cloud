from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import BigInteger, String, ForeignKey, select
import logging

from dotenv import load_dotenv
import os

load_dotenv()

db_dns = os.getenv("PG_LINK")

engine = create_async_engine(db_dns, echo=True)  # echo=True для логов SQL-запросов
print("🔍 Database URL:", db_dns)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

class Base(DeclarativeBase):
    pass

class Users(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(BigInteger,primary_key=True)
    username: Mapped[str] = mapped_column(String)
    user_status: Mapped[str] = mapped_column(String)

class File_info(Base):
    __tablename__ = "file_info"

    file_id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.user_id'))

class DatabaseManager:
    def __init__(self):
        self.session_factory = SessionLocal 

    async def add_user(self, user_id: int, user_status: str, username: str):
        async with self.session_factory() as session:
            async with session.begin():
                user = Users(user_id=user_id, user_status=user_status, username=username)
                session.add(user)

    async def add_file(self, user_id: int, file_id: str):
        async with self.session_factory() as session:
            async with session.begin():
                file_info = File_info(user_id=user_id, file_id=file_id)
                session.add(file_info)

    async def get_file_id(self, user_id: int):
        async with self.session_factory() as session:
            async with session.begin():
                result = await session.execute(
                    select(File_info.file_id).where(File_info.user_id == user_id)
                )
                files = result.scalar().all()
                return files

    async def connect(self):
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)  # Создаём таблицы
            logging.info("✅ Подключение к базе данных успешно!")
        except Exception as e:
            logging.error(f"❌ Ошибка подключения к БД: {e}")

    async def close(self):
        await engine.dispose()
        logging.info("🔌 Соединение с БД закрыто")

db = DatabaseManager()