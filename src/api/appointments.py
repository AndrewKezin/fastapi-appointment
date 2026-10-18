from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.schemas.appointments import AppointmentBaseSchema
from src.services.appointment_service import AppointmentService

router = APIRouter(
    prefix="/appointments",
    tags=["Appointments"]
)

@router.post("/")
async def create_appointment(data: AppointmentBaseSchema, session: AsyncSession = Depends(get_session)):
    service = AppointmentService(session)
    appointment = await service.create_appointment(data)
    return {"data": appointment}

@router.get("/date/{scheduled_at}")
async def get_appointments_by_date(scheduled_at: datetime, session: AsyncSession = Depends(get_session)):
    service = AppointmentService(session)
    appointments = await service.get_appointments_by_date(scheduled_at)
    return {"data": appointments}

@router.get("/")
async def get_all_appointments(session: AsyncSession = Depends(get_session)):
    service = AppointmentService(session)
    appointments = await service.get_all_appointments()
    return {"data": appointments}