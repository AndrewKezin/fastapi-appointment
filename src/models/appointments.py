from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, Enum as SQLEnum, ForeignKey
from uuid import uuid4, UUID  # <-- нужен именно Python-тип UUID
from sqlalchemy import UUID as SQLAlchemyType  # <-- это тип для колонки, не для Mapped
# from sqlalchemy.dialects.postgresql import UUID as PGUUID

from datetime import datetime
from src.database import Base

from src.schemas.appointments import AppointmentStatus

class AppointmentModel(Base):
    __tablename__ = "appointments"

    id: Mapped[UUID] = mapped_column(SQLAlchemyType, default=uuid4, primary_key=True)
    scheduled_at: Mapped[datetime]
    duration_minutes: Mapped[int | None]
    status: Mapped[AppointmentStatus] = mapped_column(SQLEnum(AppointmentStatus), default=AppointmentStatus.PENDING)
    notes: Mapped[str] = mapped_column(String(500), nullable=False)

    # связь с машиной (одна машина -> много записей)
    car_id: Mapped[UUID] = mapped_column(ForeignKey("cars.id", ondelete="CASCADE"), nullable=False)
    car: Mapped["CarModel"] = relationship(back_populates="appointments")



