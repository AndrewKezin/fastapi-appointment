from typing import List
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import check_car_owner_or_manager, check_car_owner_or_staff
from src.models.appointments import AppointmentModel
from src.models.cars import CarModel
from src.models.users import UserModel
from src.repositories.appointment_repo import AppointmentRepository
from src.repositories.car_repo import CarRepository
from src.schemas.appointments import (
    AppointmentCreateSchema,
    AppointmentSearchQueryParams,
    AppointmentUpdateSchema,
    AppointmentStatusEnum,
)
from src.schemas.users import UserRoleEnum


class AppointmentService:
    def __init__(self, session: AsyncSession):
        self.repo = AppointmentRepository(session)
        self.car_repo = CarRepository(session)

    async def _get_appointment_and_car(
        self, appointment_id: str
    ) -> tuple[CarModel, AppointmentModel]:
        appointment = await self.repo.get_app_by_id(appointment_id)
        if not appointment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Запись не найдена"
            )
        car = await self.car_repo.get_car_by_id_with_owners(appointment.car_id)
        if not car:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Автомобиль не найден"
            )
        return car, appointment

    async def create_appointment(
        self,
        data: AppointmentCreateSchema,
        current_user: UserModel,
    ) -> AppointmentModel:
        # Проверка на существование автомобиля по id
        car = await self.car_repo.get_car_by_id_with_owners(data.car_id)
        if not car:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Автомобиль с id {data.car_id} не найден",
            )

        # Проверка прав: владелец авто, менеджер или админ (выбросит 403 при отказе)
        check_car_owner_or_manager(car, current_user)

        if (
            current_user.role in (UserRoleEnum.USER, UserRoleEnum.MECHANIC)
            and "duration_minutes" in data.model_fields_set
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Предполагаемое время выполнения работ может менять только менеджер",
            )

        app_data = data.model_dump()

        new_appointment = await self.repo.create_appointment(app_data)

        if not new_appointment:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Не удалось создать запись",
            )

        return new_appointment

    async def get_appointments_by_id(
        self, appointment_id: str, current_user: UserModel
    ) -> AppointmentModel:
        car, appointment = await self._get_appointment_and_car(appointment_id)

        check_car_owner_or_staff(car, current_user)
        return appointment

    async def get_appointments(
        self, filters: AppointmentSearchQueryParams
    ) -> List[AppointmentModel]:
        result = await self.repo.get_app_list(filters)

        return result

    async def update_appointment(
        self,
        appointment_id: str,
        data: AppointmentUpdateSchema,
        current_user: UserModel,
    ) -> AppointmentModel:
        car, appointment = await self._get_appointment_and_car(appointment_id)

        # проверка прав доступа
        check_car_owner_or_staff(car, current_user)

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

        # Запрет изменения статуса записи клиентом
        if current_user.role == UserRoleEnum.USER:
            if "status" in update_data:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Клиент не может изменять статус записи",
                )
            if "duration_minutes" in update_data:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Клиент не может изменить время выполнения работ",
                )
            if (
                "scheduled_at" in update_data
                and appointment.status != AppointmentStatusEnum.PENDING
            ):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Запись уже подтверждена. Для изменения времени записи обратитесь к менеджеру.",
                )

        if current_user.role == UserRoleEnum.MECHANIC:
            if "scheduled_at" in update_data:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Механик не может изменять время записи",
                )
            if update_data.get("status") in (
                AppointmentStatusEnum.CONFIRMED,
                AppointmentStatusEnum.CANCELLED,
            ):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Механик не может подтвердить или отменить запись",
                )
            if "duration_minutes" in update_data:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Механик не может изменить время выполнения работ",
                )

        updated_app = await self.repo.update_appointment(appointment, update_data)
        if not updated_app:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Не удалось обновить запись",
            )

        return updated_app

    async def cancel_appointment(
        self, appointment_id: str, current_user: UserModel
    ) -> AppointmentModel:
        car, appointment = await self._get_appointment_and_car(appointment_id)

        check_car_owner_or_manager(car, current_user)

        if appointment.status == AppointmentStatusEnum.COMPLETED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Нельзя отменить уже выполненный ремонт",
            )

        if (
            current_user.role == UserRoleEnum.USER
            and appointment.status != AppointmentStatusEnum.PENDING
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Запись уже подтверждена. Для отмены обратитесь к менеджеру техцентра",
            )

        cancelled_app = await self.repo.update_appointment(
            appointment, {"status": AppointmentStatusEnum.CANCELLED}
        )

        return cancelled_app
