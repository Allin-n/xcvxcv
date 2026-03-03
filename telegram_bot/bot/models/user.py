from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class UserModel(BaseModel):
    """Модель пользователя для валидации"""
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_admin: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)


class VictimModel(BaseModel):
    """Модель жертвы"""
    victim_id: str
    ip_address: Optional[str] = None
    hostname: Optional[str] = None
    username: Optional[str] = None
    os_version: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    first_seen: datetime = Field(default_factory=datetime.utcnow)
    last_seen: datetime = Field(default_factory=datetime.utcnow)
    is_online: bool = False


class LogEntryModel(BaseModel):
    """Модель лога"""
    victim_id: str
    log_type: str
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)