from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.schemas.appointments import (
    AppointmentResponseSchema,
    AppointmentCreateSchema,
    AppointmentStatusEnum,
    AppointmentUpdateSchema,
)
from src.services.appointment_service import AppointmentService

router = APIRouter(prefix="/appointments", tags=["Appointments"])


def get_appointment_service(
    session: AsyncSession = Depends(get_session),
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
    service: AppointmentService = Depends(get_appointment_service),
):
    return await service.create_appointment(data)


"""
    • Path — берет данные из самого пути URL (/cars/{car_id}).
    • Query — берет параметры после знака вопроса (/cars?brand=Audi).
    • Body (или Pydantic-схема) — берет данные из JSON-тела запроса.

"""
@router.get(
    "/",
    response_model=List[AppointmentResponseSchema],
    summary="Получить список записей с фильтрацией",
)
async def get_appointments(
    car_id: Optional[str] = Query(None, description="Фильтр по ID автомобиля"),
    status_filter: Optional[AppointmentStatusEnum] = Query(
        None, alias="status", description="Фильтр по статусу"
    ),
    date_from: Optional[datetime] = Query(None, description="Начало периода"),
    date_to: Optional[datetime] = Query(None, description="Конец периода"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: AppointmentService = Depends(get_appointment_service),
):
    return await service.get_appointments(
        car_id=car_id,
        status_filter=status_filter,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/{appointment_id}",
    response_model=AppointmentResponseSchema,
    summary="Получить детали записи на ремонт",
)
async def get_appointment(
    appointment_id: str,
    service: AppointmentService = Depends(get_appointment_service),
):
    return await service.get_appointments_by_id(appointment_id)


@router.patch(
    "/{appointment_id}",
    response_model=AppointmentResponseSchema,
    summary="Обновить время, статус или описание записи",
)
async def update_appointment(
    appointment_id: str,
    data: AppointmentUpdateSchema,
    service: AppointmentService = Depends(get_appointment_service),
):
    return await service.update_appointment(appointment_id, data)


@router.post(
    "/{appointment_id}/cancel",
    response_model=AppointmentResponseSchema,
    summary="Отменить запись на ремонт",
)
async def cancel_appointment(
    appointment_id: str,
    service: AppointmentService = Depends(get_appointment_service),
):
    return await service.cancel_appointment(appointment_id)
