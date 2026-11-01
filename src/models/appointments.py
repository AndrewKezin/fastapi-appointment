from typing import TYPE_CHECKING
from datetime import datetime
from uuid import uuid4

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Enum as SQLEnum, ForeignKey

from src.database import Base
from src.schemas.appointments import AppointmentStatusEnum
from src.models.helpers import utcnow


# Импорт моделей ТОЛЬКО для проверки типов. В коде этого импорта не происходит, иначе создается циклическая зависимость
if TYPE_CHECKING:
    from src.models.cars import CarModel


class AppointmentModel(Base):
    __tablename__ = "appointments"

    id: Mapped[str] = mapped_column(
        String(36), default=lambda: str(uuid4()), primary_key=True
    )
    scheduled_at: Mapped[datetime] = mapped_column(nullable=False)
    duration_minutes: Mapped[int | None] = mapped_column(Integer, default=None)
    status: Mapped[AppointmentStatusEnum] = mapped_column(
        SQLEnum(AppointmentStatusEnum),
        default=AppointmentStatusEnum.PENDING,
    )
    notes: Mapped[str] = mapped_column(String(500), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        default=utcnow, nullable=False, onupdate=utcnow
    )

    # связь с машиной (одна машина -> много записей)
    car_id: Mapped[str] = mapped_column(
        ForeignKey("cars.id", ondelete="CASCADE"), nullable=False
    )
    # связь с машиной. Это ссылка только для ORM. В БД она никак не отражается, там только внешние ключи.
    car: Mapped["CarModel"] = relationship(
        back_populates="appointments",
        lazy="raise"  # Вызовет понятное исключение, если связь не подгружена заранее
    )
