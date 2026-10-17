from typing import Optional
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field
from enum import Enum

class UserRoleEnum(Enum):
    USER = "user"
    ADMIN = "admin"


class UserBaseSchema(BaseModel):
    email: EmailStr = Field(..., description="Электронная почта")
    first_name: str = Field(..., min_length=2, max_length=50, description="Имя")
    middle_name: Optional[str] = Field(None, min_length=2, max_length=50, description="Отчество")
    last_name: str = Field(..., min_length=2, max_length=50, description="Фамилия")
    phone: str = Field(..., min_length=10, max_length=15, description="Номер телефона с префиксом")
    address: str = Field(..., min_length=10, max_length=200, description="Адрес")

class UserCreateSchema(UserBaseSchema):
    password: str = Field(..., min_length=5, max_length=100, description="Пароль минимум 5 символов")

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