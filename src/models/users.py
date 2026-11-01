from datetime import datetime
from typing import List, TYPE_CHECKING
from uuid import uuid4

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Boolean, String, Enum as SQLEnum

from src.database import Base
from src.schemas.users import UserRoleEnum
from src.models.helpers import utcnow


# Импорт моделей ТОЛЬКО для проверки типов. В коде этого импорта не происходит, иначе создается циклическая зависимость
if TYPE_CHECKING:
    from src.models.cars import CarModel
    from src.models.ownership import UserCarOwnership

class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36), default=lambda: str(uuid4()), primary_key=True
    )
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    middle_name: Mapped[str | None] = mapped_column(String(50), default=None)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    phone: Mapped[str] = mapped_column(String(15), nullable=False)
    address: Mapped[str] = mapped_column(String(200), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    role: Mapped[UserRoleEnum] = mapped_column(
        SQLEnum(UserRoleEnum), default=UserRoleEnum.USER
    )
    created_at: Mapped[datetime] = mapped_column(default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        default=utcnow, onupdate=utcnow, nullable=False
    )

    # связь с cars "многие ко многим" через таблицу ownerships
    ownerships: Mapped[List["UserCarOwnership"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="raise"  # Вызовет понятное исключение, если связь не подгружена заранее
    )

    # Удобный «прямой» список машин через связь
    @property
    def cars(self) -> List["CarModel"]:
        return [own.car for own in self.ownerships]
