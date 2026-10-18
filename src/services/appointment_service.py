from datetime import datetime
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.appointments import AppointmentModel
from src.repositories.appointment_repo import AppointmentRepository
from src.schemas.appointments import AppointmentBaseSchema, AppointmentResponseSchema

class AppointmentService:
    def __init__(self, session: AsyncSession):
        self.repo = AppointmentRepository(session)

    async def create_appointment(self, data: AppointmentBaseSchema) -> AppointmentResponseSchema:
        appointment = await self.repo.create_appointment(data.model_dump())

        return AppointmentResponseSchema.model_validate(appointment)

    async def get_appointments_by_date(self, scheduled_at: datetime) -> List[AppointmentResponseSchema]:
        result = await self.repo.get_appointments_by_date(scheduled_at)

        if len(result) == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Записи не найдены")

        return [AppointmentResponseSchema.model_validate(appointment) for appointment in result]

    async def get_all_appointments(self) -> List[AppointmentResponseSchema]:
        result = await self.repo.get_all(AppointmentModel)

        if len(result) == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Записи не найдены")

        return [AppointmentResponseSchema.model_validate(appointment) for appointment in result]