from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import BigInteger, String, ForeignKey, select, delete
import logging
from sqlalchemy.exc import IntegrityError
import asyncpg.exceptions

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
    folder: Mapped[str] = mapped_column(String)
    file_hash: Mapped[str] = mapped_column(String)
    file_type: Mapped[str] = mapped_column(String)

class Folders(Base):
    __tablename__ = "folders"

    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.user_id'))
    folder: Mapped[str] = mapped_column(String, primary_key= True)

class DatabaseManager:
    def __init__(self):
        self.session_factory = SessionLocal 

    async def add_user(self, user_id: int, user_status: str, username: str):
        async with self.session_factory() as session:
            async with session.begin():
                user = Users(user_id=user_id, user_status=user_status, username=username)
                session.add(user)
    
    async def is_user_registered(self, user_id: int):
        async with self.session_factory() as session:
            async with session.begin():
                result = await session.execute(
                    select(Users.user_id).where(Users.user_id == user_id)
                )
                user_ids = result.scalars().all() is not None
                return user_ids

    async def add_file(self, user_id: int, file_id: str, folder: str, file_hash: str, file_type: str):
        try:
            async with self.session_factory() as session:
                async with session.begin():
                    new_file = File_info(file_id=file_id, user_id=user_id, folder=folder, file_hash=file_hash, file_type=file_type)
                    session.add(new_file)
                    await session.commit()  
        except IntegrityError as e:
            await session.rollback()  
            if isinstance(e.orig, asyncpg.exceptions.UniqueViolationError):
                return "Файл уже существует в базе"
            else:
                raise
        finally:
            await session.close()

    async def get_file(self, user_id: int, folder: str):
        async with self.session_factory() as session:
            async with session.begin():
                result = await session.execute(
                    select(File_info.file_id, File_info.file_type).where(File_info.user_id == user_id, File_info.folder == folder)
                )
                files = result.all()
                return files
                
    async def get_folders_by_id(self, user_id: int):
        async with self.session_factory() as session:
            async with session.begin():
                result = await session.execute(
                    select(Folders.folder).where(Folders.user_id == user_id).distinct()  
                )
                folders = result.scalars().all()
                return folders
            
    async def create_new_folder(self, user_id: int, folder: str):
        async with self.session_factory() as session:
            async with session.begin():
                folder = Folders(user_id=user_id, folder=folder)
                session.add(folder)

    async def delete_folder(self, user_id: int, folder: str):
        async with self.session_factory() as session:
            async with session.begin():
                await session.execute(
                    delete(File_info)
                    .where(File_info.user_id==user_id, File_info.folder==folder)
                )
                await session.execute(
                    delete(Folders)
                    .where(Folders.user_id==user_id, Folders.folder==folder)
                )

    async def unique_error_handler(self, user_id: int, file_hash: str):
        async with self.session_factory() as session:
            async with session.begin():
                try:
                    result = await session.execute(
                        select(File_info.folder).where(
                            File_info.file_hash==file_hash, 
                            File_info.user_id==user_id
                            )
                    )
                    folder = result.scalars().first()
                    if folder:
                        return folder    
                    return None
                except Exception as e:
                    print(f"Ошибка при проверке уникальности файла: {e}")
                    return None
                
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