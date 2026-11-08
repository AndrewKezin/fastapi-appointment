from __future__ import annotations

from typing import List, Optional, TYPE_CHECKING
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field
from enum import Enum

if TYPE_CHECKING:
    from src.schemas.cars import CarByUserResponseSchema


class UserRoleEnum(Enum):
    USER = "user"
    ADMIN = "admin"


class UserBaseSchema(BaseModel):
    email: EmailStr = Field(..., description="Электронная почта")
    first_name: str = Field(..., min_length=2, max_length=50, description="Имя")
    middle_name: Optional[str] = Field(
        None, min_length=2, max_length=50, description="Отчество"
    )
    last_name: str = Field(..., min_length=2, max_length=50, description="Фамилия")
    phone: str = Field(
        ..., min_length=10, max_length=15, description="Номер телефона с префиксом"
    )
    address: str = Field(..., min_length=10, max_length=200, description="Адрес")


class UserCreateSchema(UserBaseSchema):
    password: str = Field(
        ..., min_length=5, max_length=100, description="Пароль минимум 5 символов"
    )

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "email": "test@testmail.com",
                "first_name": "Иван",
                "middle_name": "Иванович",
                "last_name": "Иванов",
                "phone": "9991234567",
                "address": "г.Подольск, ул.Маркса, д.500, кв.500",
                "password": "testpass123",
            }
        },
    }


class UserChangeRoleSchema(UserBaseSchema):
    role: UserRoleEnum = UserRoleEnum.USER


class UserResponseSchema(UserBaseSchema):
    id: str
    is_active: bool
    role: UserRoleEnum
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserMinResponseSchema(BaseModel):
    id: str
    email: EmailStr
    first_name: str
    last_name: str

    model_config = {
        "from_attributes": True,  # Чтобы схема умела читать объекты SQLAlchemy
    }


class UserWithCarsResponseSchema(UserResponseSchema):
    cars: List["CarByUserResponseSchema"] = None

    model_config = {
        "from_attributes": True  # Чтобы схема умела читать объекты SQLAlchemy
    }
