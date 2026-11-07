from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.schemas.cars import CarBaseSchema, CarCreateSchema, CarResponseSchema
from src.services.car_service import CarService


router = APIRouter(prefix="/cars", tags=["Cars"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=CarResponseSchema)
async def add_car_with_owner(data: CarCreateSchema, session: AsyncSession = Depends(get_session)):
    service = CarService(session)
    new_car = await service.add_new_car_with_owner(data)
    return {"data": new_car}


@router.get("/")
async def get_all_cars_with_owners(session: AsyncSession = Depends(get_session)):
    service = CarService(session)
    cars_with_owners = await service.get_all_cars_with_owners()
    return {"data": cars_with_owners}


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
async def get_car_by_reg_number(
    reg_number: str, session: AsyncSession = Depends(get_session)
):
    service = CarService(session)
    car = await service.get_car_by_reg_number(reg_number)
    return {"data": car}
