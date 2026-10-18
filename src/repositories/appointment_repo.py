from datetime import datetime
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from src.models.appointments import AppointmentModel
from src.repositories.base_repo import BaseRepository


class AppointmentRepository(BaseRepository):
    def __init__(self, session:AsyncSession):
        super().__init__(session)

    async def create_appointment(self, data: dict) -> AppointmentModel:
        appointment = AppointmentModel(**data)
        self.session.add(appointment)
        await self.session.commit()
        await self.session.refresh(appointment)

        return appointment

    async def get_appointments_by_date(self, scheduled_at: datetime) -> List[AppointmentModel]:
        result = await self.session.execute(select(AppointmentModel).where(AppointmentModel.scheduled_at == scheduled_at))
        return list(result.scalars().all())

    