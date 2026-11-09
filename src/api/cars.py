from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.schemas.cars import CarCreateSchema, CarResponseSchema, CarSearchQueryParams
from src.services.car_service import CarService
from src.schemas.users import UserMinResponseSchema

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


@router.get("/count", status_code=status.HTTP_200_OK, response_model=dict[str, int])
async def get_count_cars(session: AsyncSession = Depends(get_session)):
    service = CarService(session)
    car_count = await service.get_count_cars()
    return {"count": car_count}


@router.get(
    "/search", status_code=status.HTTP_200_OK, response_model=List[CarResponseSchema]
)
async def search_cars(
    params: CarSearchQueryParams = Depends(),
    session: AsyncSession = Depends(get_session),
):
    service = CarService(session)

    # Передаем параметры из Pydantic-схемы напрямую в сервис
    cars = await service.search_cars(
        vin_number=params.vin_number,
        reg_number=params.reg_number,
        brand=params.brand,
        model=params.model,
        limit=params.limit,
        offset=params.offset,
    )
    return cars


# ДИНАМИЧЕСКЕ РОУТЫ В САМОМ НИЗУ, ИНАЧЕ ОНИ БУДУТ ПЕРЕХВАТЫВАТЬ СТАТИЧЕСКИЕ, РАСПОЛОЖЕННЫЕ НИЖЕ
@router.get(
    "/{car_id}", status_code=status.HTTP_200_OK, response_model=CarResponseSchema
)
async def get_car_by_id_with_owners(
    car_id: str, session: AsyncSession = Depends(get_session)
):
    service = CarService(session)
    car = await service.get_car_by_id_with_owners(car_id)
    return car


CarResponseSchema.model_rebuild()
