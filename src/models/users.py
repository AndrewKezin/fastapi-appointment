from datetime import datetime, timezone

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Enum as SQLEnum
from uuid import uuid4
# from sqlalchemy.dialects.postgresql import UUID as PGUUID


from src.database import Base
from src.schemas.users import UserRoleEnum

def utcnow():
    return datetime.now(timezone.utc)

class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), default=lambda: str(uuid4()), primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(100), nullable=False)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    middle_name: Mapped[str | None] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    phone: Mapped[str] = mapped_column(String(15), nullable=False)
    address: Mapped[str] = mapped_column(String(200), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    role: Mapped[UserRoleEnum] = mapped_column(SQLEnum(UserRoleEnum), default=UserRoleEnum.USER)
    created_at: Mapped[datetime] = mapped_column(default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(default=utcnow, onupdate=utcnow, nullable=False)

    # связь с cars "многие ко многим" через таблицу ownerships
    ownerships: Mapped[list["UserCarOwnership"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    # Удобный «прямой» список машин через связь
    @property
    def cars(self) -> list["CarModel"]:
        return [own.car for own in self.ownerships]



    