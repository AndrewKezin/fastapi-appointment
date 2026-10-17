from datetime import datetime, timezone

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Enum as SQLEnum, ForeignKey
from uuid import uuid4

from src.database import Base
from src.schemas.appointments import AppointmentStatusEnum

def utcnow():
    return datetime.now(timezone.utc)

class AppointmentModel(Base):
    __tablename__ = "appointments"

    id: Mapped[str] = mapped_column(String(36), default=lambda: str(uuid4()), primary_key=True)
    scheduled_at: Mapped[datetime]
    duration_minutes: Mapped[int | None]
    status: Mapped[AppointmentStatusEnum] = mapped_column(SQLEnum(AppointmentStatusEnum), default=AppointmentStatusEnum.PENDING)
    notes: Mapped[str] = mapped_column(String(500), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(default=utcnow, nullable=False, onupdate=utcnow)

    # связь с машиной (одна машина -> много записей)
    car_id: Mapped[str] = mapped_column(ForeignKey("cars.id", ondelete="CASCADE"), nullable=False)
    car: Mapped["CarModel"] = relationship(back_populates="appointments")



