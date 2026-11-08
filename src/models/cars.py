from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from uuid import uuid4

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import CheckConstraint, Float, String, Integer

from src.database import Base
from src.models.helpers import utcnow

# Импорт моделей ТОЛЬКО для проверки типов. В коде этого импорта не происходит, иначе создается циклическая зависимость
if TYPE_CHECKING:
    from src.models.ownership import UserCarOwnership, UserModel, AppointmentModel


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
    year: Mapped[int | None] = mapped_column(Integer, default=None)
    engine_volume: Mapped[float | None] = mapped_column(Float, default=None)
    color: Mapped[str | None] = mapped_column(String(30), default=None)
    created_at: Mapped[datetime] = mapped_column(
        default=utcnow,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=utcnow,
        onupdate=utcnow,  # при обновлении строки будет вызван utcnow()
        nullable=False,
    )

    # связь с users "многие ко многим" через ассоциативную таблицу ownerships. По факту эта связь выглядит как один car ко многим в асссоциативной таблице user_car_ownership.
    ownerships: Mapped[List["UserCarOwnership"]] = relationship(
        back_populates="car",
        cascade="all, delete-orphan",
        lazy="raise"  # Вызовет понятное исключение, если связь не подгружена заранее
    )

    # обратная связь к appointments
    appointments: Mapped[List["AppointmentModel"]] = relationship(
        back_populates="car", 
        cascade="all, delete-orphan",
        lazy="raise"
    )

    # удобный прямой доступ к пользователям
    @property
    def users(self) -> List["UserModel"]:
        return [own.user for own in self.ownerships]


    @property
    def owner(self) -> Optional["UserModel"]:
        # Проходим по записям владения в поисках основной
        for ownership in self.ownerships:
            if ownership.is_primary:
                return ownership.user  # Возвращаем связанный объект UserModel

        # Если основного нет, берем первого владельца из списка
        if self.ownerships:
            return self.ownerships[0].user

        return None

    # __table_args__ - это кортеж, поэтому в конце кортежа обязательно нужно поставить запятую
    __table_args__ = (
        CheckConstraint("length(vin_number) = 17"),  # для SQLite
        # CheckConstraint("char_length(vin_number) = 17"), # для PostgreSQL
    )
