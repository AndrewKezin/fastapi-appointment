from __future__ import annotations

import re
from datetime import datetime
from typing import Annotated, Any, List, Optional, TYPE_CHECKING

from pydantic import AfterValidator, BaseModel, Field, field_validator

from src.schemas.users import UserMinResponseSchema, UserResponseSchema

# if TYPE_CHECKING:
#     from src.schemas.users import UserMinResponseSchema, UserResponseSchema


TRANSLIT_MAP = {
    "A": "А",
    "B": "В",
    "E": "Е",
    "K": "К",
    "M": "М",
    "H": "Н",
    "O": "О",
    "P": "Р",
    "C": "С",
    "T": "Т",
    "Y": "У",
    "X": "Х",
}


# Валидатор для автоматического перевода VIN в верхний регистр
def uppercase_vin(value: Any) -> Any:
    if isinstance(value, str):
        return value.strip().upper()
    return value


# Валидатор для автоматического перевода госномера в верхний регистр и перевода случайных латинских букв в кириллицу
def validate_and_fix_reg_number(value: Any) -> Any:
    if value is None:
        return None

    if not isinstance(value, str):
        raise ValueError("Госномер должен быть строкой")

    uppercased_value = value.strip().upper()

    fixed_reg_number = "".join(
        TRANSLIT_MAP.get(char, char) for char in uppercased_value
    )

    if not re.match(r"^[АВЕКМНОРСТУХ0-9]+$", fixed_reg_number):
        raise ValueError(
            "Госномер содержит недопустимые символы. Разрешены только цифры и буквы: А, В, Е, К, М, Н, О, Р, С, Т, У, Х."
        )
    return fixed_reg_number


# Создаем переиспользуемые типы с привязанными валидаторами
VinStr = Annotated[str, AfterValidator(uppercase_vin)]
RegNumberStr = Annotated[str, AfterValidator(validate_and_fix_reg_number)]


class CarBaseSchema(BaseModel):
    vin_number: VinStr = Field(
        ...,
        min_length=17,
        max_length=17,
        description="Уникальный VIN-номер автомобиля (17 символов)",
    )
    reg_number: RegNumberStr = Field(
        ..., min_length=6, max_length=10, description="Регистрационный номер (госномер)"
    )
    brand: str = Field(..., min_length=2, max_length=50, description="Марка автомобиля")
    model: str = Field(..., max_length=50, description="Модель автомобиля")
    year: Optional[int] = Field(
        None, ge=1950, le=datetime.now().year + 1, description="Год выпуска автомобиля"
    )
    engine_volume: Optional[float] = Field(
        None, gt=0.0, lt=8.0, description="Объем двигателя в литрах (например, 2.0)"
    )
    color: Optional[str] = Field(None, max_length=30, description="Цвет автомобиля")

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
                "year": 2015,
                "engine_volume": 3.0,
                "color": "Красный",
                "owner_id": "47f43c2d-a4d1-436d-b52b-51e436f0d555",
            }
        },
    }


class CarResponseSchema(CarBaseSchema):
    id: str

    # Вместо owner_id отдаем целый объект владельца!
    owner: Optional["UserMinResponseSchema"] = None
    users: List["UserResponseSchema"] = []

    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CarByUserResponseSchema(CarBaseSchema):
    id: str

    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CarSearchQueryParams(BaseModel):
    vin_number: Optional[str] = Field(
        None,
        min_length=7,
        max_length=17,
        description="Поиск по полному VIN (минимум 7 символов)",
    )
    reg_number: Optional[str] = Field(
        None,
        min_length=3,
        max_length=10,
        description="Поиск по госномеру (минимум 3 цифры)",
    )
    brand: Optional[str] = Field(
        None, min_length=2, max_length=50, description="Фильтр по марке"
    )
    model: Optional[str] = Field(
        None, min_length=2, max_length=50, description="Фильтр по модели"
    )

    # пагинация
    limit: int = Field(
        10, ge=1, le=100, description="Количество записей на страницу (макс. 100)"
    )
    offset: int = Field(
        0, ge=0, description="Количество пропускаемых записей (смещение)"
    )

    @field_validator("vin_number", "reg_number", "brand", "model")
    @classmethod
    def uppercase_search_fields(cls, value: Optional[str]) -> Optional[str]:
        return value.upper() if value else None


class CarUpdateSchema(BaseModel):
    vin_number: Optional[VinStr] = Field(
        None,
        min_length=17,
        max_length=17,
        description="Уникальный VIN-номер автомобиля (17 символов)",
    )
    reg_number: Optional[RegNumberStr] = Field(
        None,
        min_length=6,
        max_length=10,
        description="Регистрационный номер (госномер)",
    )
    brand: Optional[str] = Field(
        None, min_length=2, max_length=50, description="Марка автомобиля"
    )
    model: Optional[str] = Field(None, max_length=50, description="Модель автомобиля")
    year: Optional[int] = Field(
        None, ge=1950, le=datetime.now().year + 1, description="Год выпуска автомобиля"
    )
    engine_volume: Optional[float] = Field(
        None, gt=0.0, lt=8.0, description="Объем двигателя в литрах (например, 2.0)"
    )
    color: Optional[str] = Field(None, max_length=30, description="Цвет автомобиля")

    owner_id: Optional[str] = Field(None, description="ID пользователя")
    is_primary_owner: bool = Field(
        False,
        description="True — сделать основным владельцем, False — добавить как дополнительного",
    )

    model_config = {
        "from_attributes": True  # Чтобы схема умела читать объекты SQLAlchemy
    }
