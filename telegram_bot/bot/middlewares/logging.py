from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
import logging
import time

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        start_time = time.time()

        # Логируем входящее сообщение
        user = event.from_user
        log_msg = f"User {user.id} (@{user.username}) sent: {event.text}"

        if event.photo:
            log_msg = f"User {user.id} sent photo"
        elif event.document:
            log_msg = f"User {user.id} sent document: {event.document.file_name}"

        logger.info(log_msg)

        # Обрабатываем
        result = await handler(event, data)

        # Логируем время обработки
        duration = time.time() - start_time
        logger.info(f"Handled in {duration:.3f}s")

        return result