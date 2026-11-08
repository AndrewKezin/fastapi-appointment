from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.schemas.cars import CarCreateSchema, CarResponseSchema
from src.services.car_service import CarService

router = APIRouter(prefix="/cars", tags=["Cars"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=CarResponseSchema)
async def add_car_with_owner(
    data: CarCreateSchema, session: AsyncSession = Depends(get_session)
):
    service = CarService(session)
    new_car = await service.add_new_car_with_owner(data)
    return new_car


@router.get("/", status_code=status.HTTP_200_OK, response_model=List[CarResponseSchema])
async def get_all_cars_with_owners(session: AsyncSession = Depends(get_session)):
    service = CarService(session)
    cars_with_owners = await service.get_all_cars_with_owners()
    return cars_with_owners


@router.get("/count")
async def get_count_cars(session: AsyncSession = Depends(get_session)):
    service = CarService(session)
    car_count = await service.get_count_cars()
    return {"count": car_count}


@router.get(
    "/{car_id}", status_code=status.HTTP_200_OK, response_model=CarResponseSchema
)
async def get_car_by_id_with_owners(
    car_id: str, session: AsyncSession = Depends(get_session)
):
    service = CarService(session)
    car = await service.get_car_by_id_with_owners(car_id)
    return car


@router.get(
    "/vin/{vin_number}",
    status_code=status.HTTP_200_OK,
    response_model=CarResponseSchema,
)
async def get_car_by_vin_with_owners(
    vin_number: str, session: AsyncSession = Depends(get_session)
):
    service = CarService(session)
    car = await service.get_car_by_vin_with_owners(vin_number)
    return car


@router.get(
    "/regnumber/{reg_number}",
    status_code=status.HTTP_200_OK,
    response_model=CarResponseSchema,
)
async def get_car_by_reg_number__with_owners(
    reg_number: str, session: AsyncSession = Depends(get_session)
):
    service = CarService(session)
    car = await service.get_car_by_reg_number_with_owners(reg_number)
    return car
