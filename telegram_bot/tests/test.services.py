import pytest
from telegram_bot.bot.services.utils import generate_victim_id, format_victim_info

def test_generate_victim_id():
    data = {"hostname": "test-pc", "username": "user"}
    victim_id = generate_victim_id(data)
    assert len(victim_id) == 32
    assert isinstance(victim_id, str)

# Добавьте больше тестов