from fastapi import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from src.database import get_session
from src.schemas.cars import CarBaseSchema
from src.services.car_service import CarService

router = APIRouter(
    prefix="/cars",
    tags=["Cars"]
)

@router.post("/")
async def add_car(data: CarBaseSchema, session: AsyncSession = Depends(get_session)):
    service = CarService(session)
    new_car = await service.add_car(data)
    return {"data": new_car}

@router.get("/")
async def get_all_cars(session: AsyncSession = Depends(get_session)):
    service = CarService(session)
    cars = await service.get_all_cars()
    return {"data": cars}

@router.get("/count")
async def get_count_cars(session: AsyncSession = Depends(get_session)):
    service = CarService(session)
    car_count = await service.get_count_cars()
    return {"data": car_count}


@router.get("/{car_id}")
async def get_car_by_id(car_id: str, session: AsyncSession = Depends(get_session)):
    service = CarService(session)
    car = await service.get_car_by_id(car_id)
    return {"data": car}

@router.get("/vin/{vin_number}")
async def get_car_by_vin(vin_number: str, session: AsyncSession = Depends(get_session)):
    service = CarService(session)
    car = await service.get_car_by_vin(vin_number)
    return {"data": car}

@router.get("/regnumber/{reg_number}")
async def get_car_by_reg_number(reg_number: str, session: AsyncSession = Depends(get_session)):
    service = CarService(session)
    car = await service.get_car_by_reg_number(reg_number)
    return {"data": car}