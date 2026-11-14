from datetime import datetime
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc, select, and_
from sqlalchemy.orm import selectinload

from src.models.appointments import AppointmentModel
from src.repositories.base_repo import BaseRepository
from src.schemas.appointments import AppointmentStatusEnum


class AppointmentRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def create_appointment(self, data: dict) -> Optional[AppointmentModel]:
        appointment = AppointmentModel(**data)
        self.session.add(appointment)

        try:
            await self.session.commit()
            return await self.get_app_by_id(appointment.id)
        except Exception as e:
            await self.session.rollback()
            print("Error creating appointment:", e)
            return None

    async def get_app_by_id(self, app_id: str) -> Optional[AppointmentModel]:
        stmt = (
            select(AppointmentModel)
            .where(AppointmentModel.id == app_id)
            .options(selectinload(AppointmentModel.car))
            .execution_options(
                populate_existing=True
            )  # отпрвить запрос, а не взять данные из кэша
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_app_list(
        self,
        car_id: Optional[str] = None,
        status: Optional[AppointmentStatusEnum] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[AppointmentModel]:
        stmt = (
            select(AppointmentModel)
            .options(selectinload(AppointmentModel.car))
            .order_by(desc(AppointmentModel.scheduled_at))
        )

        if car_id:
            stmt = stmt.where(AppointmentModel.car_id == car_id)
        if status:
            stmt = stmt.where(AppointmentModel.status == status)
        if date_from:
            stmt = stmt.where(AppointmentModel.scheduled_at >= date_from)
        if date_to:
            stmt = stmt.where(AppointmentModel.scheduled_at <= date_to)

        stmt = stmt.limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update_appointment(
        self, appointment: AppointmentModel, update_data: dict
    ) -> Optional[AppointmentModel]:
        try:
            for field, value in update_data.items():
                setattr(appointment, field, value)

            await self.session.commit()
            # сбросить кэш, чтобы при следующий запрос прочитал чистое и актуальное состояние объекта со всеми связями
            self.session.expire_all()
            return await self.session.get_app_by_id(appointment.id)
        except Exception as e:
            await self.session.rollback()
            print("Error updating appointment:", e)
            return None

    async def delete_appointment(self, appointment: AppointmentModel) -> bool:
        try:
            await self.session.delete(appointment)
            await self.session.commit()
            return True
        except Exception as e:
            await self.session.rollback()
            print("Error deleting appointment:", e)
            return False
