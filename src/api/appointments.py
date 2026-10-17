from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.schemas.appointments import AppointmentBaseSchema

router = APIRouter(
    prefix="/appointments",
    tags=["Appointments"]
)

@router.post("/")
async def add_appointment(data: AppointmentBaseSchema, session: AsyncSession = Depends(get_session)):
    pass