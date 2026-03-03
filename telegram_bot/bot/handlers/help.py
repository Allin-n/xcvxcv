from aiogram import Router, types
from aiogram.filters import Command

router = Router()


@router.message(Command("help"))
async def cmd_help(message: types.Message):
    """Обработчик команды /help"""
    help_text = (
        "🔰 <b>Справка по использованию C2 бота</b>\n\n"
        "<b>Основные команды:</b>\n"
        "• /start - Начать работу\n"
        "• /help - Показать это сообщение\n"
        "• /stats - Показать статистику\n\n"

        "<b>Управление жертвами:</b>\n"
        "• /victims - Список всех жертв\n"
        "• /online - Онлайн жертвы\n"
        "• /victim [ID] - Информация о жертве\n"
        "• /logs [ID] - Логи жертвы\n"
        "• /files [ID] - Файлы жертвы\n\n"

        "<b>Админ-команды:</b>\n"
        "• /broadcast [текст] - Рассылка админам\n"
        "• /clean [дни] - Очистка старых логов\n"
    )

    await message.answer(help_text)