from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class AppointmentStatusEnum(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class AppointmentBaseSchema(BaseModel):
    scheduled_at: datetime = Field(..., description="Дата и время записи")
    duration_minutes: Optional[int] = Field(None, gte=0, description="Предполагаемая продолжительность работ в минутах")
    notes: str = Field(..., min_length=5, max_length=500, description="Предполагаемые работы")
    car_id: str = Field(..., description="Идентификатор автомобиля")


class AppointmentChangeStatusSchema(AppointmentBaseSchema):
    status: AppointmentStatusEnum = Field(..., description="Статус записи")

class AppointmentResponseSchema(AppointmentChangeStatusSchema):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

