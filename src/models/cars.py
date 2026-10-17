from datetime import datetime, timezone

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import CheckConstraint, Float, String
from uuid import uuid4

from src.database import Base

def utcnow():
    return datetime.now(timezone.utc)

class CarModel(Base):
    __tablename__ = "cars"

    # UUID храним как строку (36 символов) — это работает везде, включая SQLite
    id: Mapped[str] = mapped_column(
        String(36),
        default=lambda: str(uuid4()),
        primary_key=True,
    )
    vin_number: Mapped[str] = mapped_column(String(17), unique=True, nullable=False)
    reg_number: Mapped[str] = mapped_column(String(8))
    brand: Mapped[str] = mapped_column(String(50))
    model: Mapped[str] = mapped_column(String(50))
    engine_volume: Mapped[float | None] = mapped_column(default=None)
    color: Mapped[str | None] = mapped_column(default=None)
    created_at: Mapped[datetime] = mapped_column(
        default=utcnow,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=utcnow,
        onupdate=utcnow,  # при обновлении строки будет вызван utcnow()
        nullable=False,
    )

    # связь с users "многие ко многим" через таблицу ownerships
    ownerships: Mapped[list["UserCarOwnership"]] = relationship(
        back_populates="car",
        cascade="all, delete-orphan",
    )

    # удобный прямой доступ к пользователям
    @property
    def users(self) -> list["UserModel"]:
        return [own.user for own in self.ownerships]

    # обратная связь к appointments
    appointments: Mapped[list["AppointmentModel"]] = relationship(back_populates="car", cascade="all, delete-orphan")

    # __table_args__ - это кортеж, поэтому в конце кортежа обязательно нужно поставить запятую
    __table_args__ = (
        CheckConstraint("length(vin_number) = 17"), # для SQLite
        # CheckConstraint("char_length(vin_number) = 17"), # для PostgreSQL
    )