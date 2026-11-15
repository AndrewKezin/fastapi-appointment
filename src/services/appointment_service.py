from datetime import datetime
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.appointments import AppointmentModel
from src.repositories.appointment_repo import AppointmentRepository
from src.repositories.car_repo import CarRepository
from src.schemas.appointments import (
    AppointmentCreateSchema,
    AppointmentSearchQueryParams,
    AppointmentUpdateSchema,
    AppointmentStatusEnum,
)


class AppointmentService:
    def __init__(self, session: AsyncSession):
        self.repo = AppointmentRepository(session)
        self.car_repo = CarRepository(session)

    async def create_appointment(
        self, data: AppointmentCreateSchema
    ) -> AppointmentModel:
        # Проверка на существование автомобиля по id
        car = await self.car_repo.get_car_by_id_with_owners(data.car_id)
        if not car:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Автомобиль с id {data.car_id} не найден",
            )

        new_appointment = await self.repo.create_appointment(data.model_dump())

        if not new_appointment:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Не удалось создать запись",
            )

        return new_appointment

    async def get_appointments_by_id(self, appointment_id: str) -> AppointmentModel:
        appointment = await self.repo.get_app_by_id(appointment_id)
        if not appointment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Запись не найдена"
            )

        return appointment

    async def get_appointments(
        self, filters: AppointmentSearchQueryParams
    ) -> List[AppointmentModel]:
        result = await self.repo.get_app_list(filters)

        return result

    async def update_appointment(
        self, appointment_id: str, data: AppointmentUpdateSchema
    ) -> AppointmentModel:
        appointment = await self.repo.get_app_by_id(appointment_id)

        # Нельзя менять отмененную или завершенную запись
        if appointment.status in (
            AppointmentStatusEnum.COMPLETED,
            AppointmentStatusEnum.CANCELLED,
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Нельзя изменить запись в статусе {appointment.status.value}",
            )

        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return appointment

        updated_app = await self.repo.update_appointment(appointment, update_data)
        if not updated_app:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Не удалось обновить запись",
            )

        return updated_app

    async def cancel_appointment(self, appointment_id: str) -> AppointmentModel:
        appointment = await self.repo.get_app_by_id(appointment_id)
        if appointment.status == AppointmentStatusEnum.COMPLETED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Нельзя отменить уже выполненный ремонт",
            )

        cancelled_app = await self.repo.update_appointment(
            appointment, {"status": AppointmentStatusEnum.CANCELLED}
        )

        return cancelled_app
