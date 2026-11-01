from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from src.schemas.users import UserMinResponseSchema


class CarBaseSchema(BaseModel):
    vin_number: str = Field(
        ...,
        min_lenght=17,
        max_lenght=17,
        description="Уникальный VIN-номер автомобиля (17 символов)",
    )
    reg_number: str = Field(
        ..., min_lenght=6, max_lenght=8, description="Регистрационный номер (госномер)"
    )
    brand: str = Field(..., min_lenght=2, max_lenght=50, description="Марка автомобиля")
    model: str = Field(..., max_length=50, description="Модель автомобиля")
    engine_volume: Optional[float] = Field(
        None, gt=0.0, lt=8.0, description="Объем двигателя в литрах (например, 2.0)"
    )
    color: Optional[str] = Field(None, max_length=30, description="Цвет автомобиля")
    # Поле для автоматической привязки владельца при создании машины
    owner_id: str = Field(
        ..., description="ID пользователя, который создается как владелец машины"
    )

    # Валидатор для автоматического перевода VIN в верхний регистр (опционально, но полезно)
    @field_validator("vin_number")
    @classmethod
    def uppercase_vin(cls, value: str) -> str:
        return value.upper()

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
                "owner_id": "d6655df9-1035-46f7-8b3e-7c0f8e57c818",
            }
        },
    }


class CarResponseSchema(CarBaseSchema):
    id: str
    vin_number: str
    reg_number: str
    brand: str
    model: str
    engine_volume: Optional[float] = None
    color: Optional[str] = None

    # Вместо owner_id отдаем целый объект владельца!
    owner: Optional[UserMinResponseSchema] = None

    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
