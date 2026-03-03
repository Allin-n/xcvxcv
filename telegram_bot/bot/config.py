import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x]
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///database/bot.db")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    # Папки для логов
    LOGS_DIR = "logs"
    UPLOADS_DIR = "uploads"

    # Проверка на существование папок
    os.makedirs(LOGS_DIR, exist_ok=True)
    os.makedirs(UPLOADS_DIR, exist_ok=True)