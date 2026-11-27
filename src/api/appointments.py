from typing import Annotated, List

from fastapi import APIRouter, Depends, Query, status

from src.api.dependencies import (
    CurrentUser,
    SessionDep,
    allow_staff,
    allow_management,
)
from src.schemas.appointments import (
    AppointmentResponseSchema,
    AppointmentCreateSchema,
    AppointmentSearchQueryParams,
    AppointmentUpdateSchema,
)
from src.services.appointment_service import AppointmentService

router = APIRouter(prefix="/appointments", tags=["Appointments"])


def get_appointment_service(
    session: SessionDep,
) -> AppointmentService:
    return AppointmentService(session)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=AppointmentResponseSchema,
    summary="Создать запись в техцентр",
)
async def create_appointment(
    data: AppointmentCreateSchema,
    current_user: CurrentUser,
    service: AppointmentService = Depends(get_appointment_service),
):
    # Проверка прав доступа производится в сервисе после загрузки данных об авто из БД
    return await service.create_appointment(data, current_user)


"""
    • Path — берет данные из самого пути URL (/cars/{car_id}).
    • Query — берет параметры после знака вопроса (/cars?brand=Audi).
    • Body (или Pydantic-схема) — берет данные из JSON-тела запроса.

"""


@router.get(
    "/",
    response_model=List[AppointmentResponseSchema],
    summary="Получить список записей с фильтрацией",
    dependencies=[Depends(allow_staff)],  # доступ только персоналу
)
async def get_appointments(
    filters: Annotated[AppointmentSearchQueryParams, Query()],
    service: AppointmentService = Depends(get_appointment_service),
):
    return await service.get_appointments(filters)


@router.get(
    "/{appointment_id}",
    response_model=AppointmentResponseSchema,
    summary="Получить детали записи на ремонт",
)
async def get_appointment(
    appointment_id: str,
    current_user: CurrentUser,
    service: AppointmentService = Depends(get_appointment_service),
):
    return await service.get_appointments_by_id(appointment_id, current_user)


@router.patch(
    "/{appointment_id}",
    response_model=AppointmentResponseSchema,
    summary="Обновить время, статус или описание записи",
)
async def update_appointment(
    appointment_id: str,
    data: AppointmentUpdateSchema,
    current_user: CurrentUser,
    service: AppointmentService = Depends(get_appointment_service),
):
    return await service.update_appointment(appointment_id, data, current_user)


@router.post(
    "/{appointment_id}/cancel",
    response_model=AppointmentResponseSchema,
    summary="Отменить запись на ремонт",
)
async def cancel_appointment(
    appointment_id: str,
    current_user: CurrentUser,
    service: AppointmentService = Depends(get_appointment_service),
):
    return await service.cancel_appointment(appointment_id, current_user)
