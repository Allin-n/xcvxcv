import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import Config
from bot.handlers import start, help, admin
from bot.middlewares.logging import LoggingMiddleware
from bot.database.db_manager import DatabaseManager

logger = logging.getLogger(__name__)


async def on_startup(bot: Bot):
    """Действия при запуске бота"""
    logger.info("Bot starting up...")

    # Инициализация базы данных
    db = DatabaseManager()
    await db.init_db()

    # Уведомление админам
    for admin_id in Config.ADMIN_IDS:
        try:
            await bot.send_message(
                admin_id,
                "Бот запущен\n"
                f"База данных: {Config.DATABASE_URL}"
            )
        except:
            pass


async def on_shutdown(bot: Bot):
    """Действия при остановке бота"""
    logger.info("Bot shutting down...")

    # Уведомление админам
    for admin_id in Config.ADMIN_IDS:
        try:
            await bot.send_message(admin_id, "Бот остановлен")
        except:
            pass


async def main():
    # Настройка логирования
    logging.basicConfig(
        level=getattr(logging, Config.LOG_LEVEL),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("logs/bot.log"),
            logging.StreamHandler()
        ]
    )

    # Инициализация бота и диспетчера
    bot = Bot(
        token=Config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=MemoryStorage())

    # Подключаем middleware
    dp.message.middleware(LoggingMiddleware())

    # Регистрируем роутеры
    dp.include_router(start.router)
    dp.include_router(help.router)
    dp.include_router(admin.router)

    # Запуск
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())