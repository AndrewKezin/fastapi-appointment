from __future__ import annotations

from datetime import datetime
from typing import Optional, TYPE_CHECKING

from pydantic import BaseModel, Field, field_validator

if TYPE_CHECKING:
    from src.schemas.users import UserMinResponseSchema


class CarBaseSchema(BaseModel):
    vin_number: str = Field(
        ...,
        min_length=17,
        max_length=17,
        description="Уникальный VIN-номер автомобиля (17 символов)",
    )
    reg_number: str = Field(
        ..., min_lenght=6, max_length=10, description="Регистрационный номер (госномер)"
    )
    brand: str = Field(..., min_length=2, max_lenght=50, description="Марка автомобиля")
    model: str = Field(..., max_length=50, description="Модель автомобиля")
    engine_volume: Optional[float] = Field(
        None, gt=0.0, lt=8.0, description="Объем двигателя в литрах (например, 2.0)"
    )
    color: Optional[str] = Field(None, max_length=30, description="Цвет автомобиля")

    # Валидатор для автоматического перевода VIN в верхний регистр (опционально, но полезно)
    @field_validator("vin_number")
    @classmethod
    def uppercase_vin(cls, value: str) -> str:
        return value.upper()

    model_config = {
        "from_attributes": True  # Чтобы схема умела читать объекты SQLAlchemy
    }

   

class CarCreateSchema(CarBaseSchema):
    # Поле для автоматической привязки владельца при создании машины
    owner_id: str = Field(
        ..., description="ID пользователя, который создается как владелец машины"
    )

    model_config = {
            "from_attributes": True,
            "json_schema_extra": {
                "example": {
                    "vin_number": "WAUZZZ4M901234567",
                    "reg_number": "А000АА00",
                    "brand": "AUDI",
                    "model": "Q7",
                    "engine_volume": 3.0,
                    "color": "Красный",
                    "owner_id": "47f43c2d-a4d1-436d-b52b-51e436f0d555"
                }
            },
        }


class CarResponseSchema(CarBaseSchema):
    id: str
    
    # Вместо owner_id отдаем целый объект владельца!
    owner: Optional["UserMinResponseSchema"] = None

    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class CarByUserResponseSchema(CarBaseSchema):
    id: str

    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
