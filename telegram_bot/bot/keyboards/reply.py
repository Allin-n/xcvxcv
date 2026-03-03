from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def main_menu_keyboard(is_admin: bool = False) -> ReplyKeyboardMarkup:
    """Главное меню"""
    builder = ReplyKeyboardBuilder()

    builder.row(
        KeyboardButton(text="📊 Статистика"),
        KeyboardButton(text="📋 Жертвы")
    )
    builder.row(
        KeyboardButton(text="🟢 Онлайн"),
        KeyboardButton(text="📝 Логи")
    )

    if is_admin:
        builder.row(
            KeyboardButton(text="📢 Рассылка"),
            KeyboardButton(text="⚙️ Настройки")
        )

    return builder.as_markup(resize_keyboard=True)


def cancel_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура с кнопкой отмены"""
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="❌ Отмена"))
    return builder.as_markup(resize_keyboard=True)