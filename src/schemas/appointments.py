from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator, model_validator

from src.models.helpers import utcnow
from src.schemas.cars import CarByUserResponseSchema


class AppointmentStatusEnum(Enum):
    PENDING = "Ожидается подтверждение записи"
    CONFIRMED = "Запись подтверждена"
    IN_PROGRESS = "Производятся работы по автомобилю"
    COMPLETED = "Работы выполнены"
    CANCELLED = "Запись отменена"


class AppointmentBaseSchema(BaseModel):
    scheduled_at: datetime = Field(..., description="Дата и время записи")
    duration_minutes: Optional[int] = Field(
        None, gte=0, description="Предполагаемая продолжительность работ в минутах"
    )
    notes: str = Field(
        ..., min_length=5, max_length=500, description="Предполагаемые работы"
    )

    # Проверить, что время записи не находится в прошлом
    @field_validator("scheduled_at")
    @classmethod
    def check_future_date(cls, value: datetime) -> datetime:
        now = utcnow()
        # Если дата от клиента пришла без часового пояса, то добавить его. Иначе упадет при сравнении
        val_utc = value if value.tzinfo else value.replace(tzinfo=timezone.utc)
        if val_utc < now:
            raise ValueError("Некорректное время записи")
        return val_utc


class AppointmentCreateSchema(AppointmentBaseSchema):
    car_id: str = Field(..., description="ID автомобиля из базы данных")


class AppointmentUpdateSchema(BaseModel):
    scheduled_at: Optional[datetime] = Field(
        None, description="Новая дата и время записи"
    )
    duration_minutes: Optional[int] = Field(None, ge=0)
    status: Optional[AppointmentStatusEnum] = Field(None, description="Статус заявки")
    notes: Optional[str] = Field(None, max_length=500)


class AppointmentResponseSchema(BaseModel):
    id: str
    car_id: str
    scheduled_at: datetime
    duration_minutes: Optional[int]
    status: AppointmentStatusEnum
    notes: str
    created_at: datetime
    updated_at: datetime
    car: Optional[CarByUserResponseSchema] = None

    model_config = {"from_attributes": True}


class AppointmentSearchQueryParams(BaseModel):
    car_id: Optional[str] = Field(None, description="Фильтр по ID автомобиля")
    status: Optional[AppointmentStatusEnum] = Field(
        None, description="Фильтр по статусу"
    )
    date_from: Optional[datetime] = Field(None, description="Начало периода")
    date_to: Optional[datetime] = Field(None, description="Конец периода")

    # Пагинация
    limit: int = Field(
        20, ge=1, le=100, description="Количество записей на страницу (макс. 100)"
    )
    offset: int = Field(
        0, ge=0, description="Количество пропускаемых записей (смещение)"
    )

    @model_validator(mode="after")
    def check_date_range(self) -> "AppointmentSearchQueryParams":
        if self.date_from and self.date_to and self.date_from > self.date_to:
            raise ValueError("Дата начала периода (date_from) не может быть позже даты окончания (date_to)")
        return self
