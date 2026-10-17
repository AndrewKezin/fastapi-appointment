from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

from src.database import Base
from datetime import datetime


# промежуточная таблица для связи user >--< car "многие ко многим". Метод - ассоциативная модель (НЕ secondary), чтобы указать дополнительные данные о связях 
class UserCarOwnership(Base):
    __tablename__ = "user_car_ownership"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    car_id: Mapped[str] = mapped_column(ForeignKey("cars.id", ondelete="CASCADE"), primary_key=True)

    ownership_start: Mapped[datetime] = mapped_column(default=datetime.utcnow) # начало владения
    ownership_end: Mapped[datetime | None] = mapped_column(nullable=True) # окончание владения

    is_primary: Mapped[bool] = mapped_column(default=True) # основной владелец

    # отношения к основным моделям
    user: Mapped["UserModel"] = relationship(back_populates="ownerships")
    car: Mapped["CarModel"] = relationship(back_populates="ownerships")
    