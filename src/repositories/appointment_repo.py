from datetime import datetime
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc, select, and_
from sqlalchemy.orm import selectinload

from src.models.appointments import AppointmentModel
from src.repositories.base_repo import BaseRepository
from src.schemas.appointments import AppointmentStatusEnum, AppointmentSearchQueryParams


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
        self, filters: AppointmentSearchQueryParams
    ) -> List[AppointmentModel]:
        stmt = (
            select(AppointmentModel)
            .options(selectinload(AppointmentModel.car))
            .order_by(desc(AppointmentModel.scheduled_at))
        )

        if filters.car_id:
            stmt = stmt.where(AppointmentModel.car_id == filters.car_id)
        if filters.status:
            stmt = stmt.where(AppointmentModel.status == filters.status)
        if filters.date_from:
            stmt = stmt.where(AppointmentModel.scheduled_at >= filters.date_from)
        if filters.date_to:
            stmt = stmt.where(AppointmentModel.scheduled_at <= filters.date_to)

        stmt = stmt.limit(filters.limit).offset(filters.offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update_appointment(
        self, appointment: AppointmentModel, update_data: dict
    ) -> Optional[AppointmentModel]:
        try:
            for field, value in update_data.items():
                setattr(appointment, field, value)

            appointment_id = appointment.id  # сохранить id до commit() и expire_all()

            await self.session.commit()
            # сбросить кэш, чтобы при следующий запрос прочитал чистое и актуальное состояние объекта со всеми связями
            self.session.expire_all()
            return await self.get_app_by_id(appointment_id)
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
