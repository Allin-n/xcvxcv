from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def victim_detail_keyboard(victim_id: str) -> InlineKeyboardMarkup:
    """Клавиатура для детальной страницы жертвы"""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="📝 Логи", callback_data=f"logs_{victim_id}"),
        InlineKeyboardButton(text="📁 Файлы", callback_data=f"files_{victim_id}")
    )
    builder.row(
        InlineKeyboardButton(text="💻 Система", callback_data=f"system_{victim_id}"),
        InlineKeyboardButton(text="📌 Заметка", callback_data=f"note_{victim_id}")
    )
    builder.row(
        InlineKeyboardButton(text="🔄 Обновить", callback_data=f"refresh_{victim_id}"),
        InlineKeyboardButton(text="❌ Удалить", callback_data=f"delete_{victim_id}")
    )

    return builder.as_markup()


def pagination_keyboard(current_page: int, total_pages: int, prefix: str) -> InlineKeyboardMarkup:
    """Клавиатура для пагинации"""
    builder = InlineKeyboardBuilder()

    buttons = []

    if current_page > 1:
        buttons.append(InlineKeyboardButton(
            text="◀️",
            callback_data=f"{prefix}_page_{current_page - 1}"
        ))

    buttons.append(InlineKeyboardButton(
        text=f"{current_page}/{total_pages}",
        callback_data="noop"
    ))

    if current_page < total_pages:
        buttons.append(InlineKeyboardButton(
            text="▶️",
            callback_data=f"{prefix}_page_{current_page + 1}"
        ))

    builder.row(*buttons)

    return builder.as_markup()


def confirm_keyboard(action: str, data: str) -> InlineKeyboardMarkup:
    """Клавиатура подтверждения"""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="✅ Да", callback_data=f"confirm_{action}_{data}"),
        InlineKeyboardButton(text="❌ Нет", callback_data=f"cancel_{action}_{data}")
    )

    return builder.as_markup()