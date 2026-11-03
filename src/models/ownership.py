from typing import TYPE_CHECKING
from datetime import datetime
from uuid import uuid4

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Boolean, DateTime, ForeignKey, String, UniqueConstraint, Index, text

from src.database import Base
from src.models.helpers import utcnow

# Импорт моделей ТОЛЬКО для проверки типов. В коде этого импорта не происходит, иначе создается циклическая зависимость
if TYPE_CHECKING:
    from src.models.cars import CarModel
    from src.models.users import UserModel

    
# промежуточная таблица для связи user >--< car "многие ко многим". Метод - ассоциативная модель (НЕ secondary), чтобы указать дополнительные данные о связях
class UserCarOwnership(Base):
    __tablename__ = "user_car_ownership"

    __table_args__ = (
        # Уникальность пары юзер-машина
        UniqueConstraint("user_id", "car_id", name="uq_user_car"),
        
        # Только один основной владелец у машины (для SQLite используем 1 вместо True)
        Index(
            "uq_primary_car_owner",
            "car_id",
            unique=True,
            sqlite_where=text("is_primary = 1")
        ),
    )

    id: Mapped[str] = mapped_column(String(36), default=lambda: str(uuid4()), primary_key=True)

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    car_id: Mapped[str] = mapped_column(
        ForeignKey("cars.id", ondelete="CASCADE"), nullable=False
    )

    ownership_start: Mapped[datetime] = mapped_column(
        DateTime, default=utcnow, nullable=False
    )  # начало владения
    ownership_end: Mapped[datetime | None] = mapped_column(
        DateTime, default=None, nullable=True
    )  # окончание владения

    is_primary: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="FALSE", nullable=False
    )  # основной владелец

    # отношения к основным моделям. В модели UserModel должно быть поле ownerships, а в нем - отношение к полю user в модели UserCarOwnership
    user: Mapped["UserModel"] = relationship(
        back_populates="ownerships",
        lazy="raise"  # Вызовет понятное исключение, если связь не подгружена заранее
    )
    car: Mapped["CarModel"] = relationship(
        back_populates="ownerships",
        lazy="raise"
    )
