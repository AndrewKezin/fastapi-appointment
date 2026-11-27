from typing import List

from fastapi import APIRouter, Depends, status

from src.schemas.cars import (
    CarCreateSchema,
    CarResponseSchema,
    CarSearchQueryParams,
    CarUpdateSchema,
)
from src.services.car_service import CarService
from src.schemas.users import UserMinResponseSchema
from src.api.dependencies import (
    CurrentUser,
    SessionDep,
    allow_management,
    check_car_owner_or_manager,
)

router = APIRouter(prefix="/cars", tags=["Cars"])


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=CarResponseSchema,
    summary="Создать автомобиль с владельцем",
)
async def add_car_with_owner(data: CarCreateSchema, session: SessionDep):
    service = CarService(session)
    new_car = await service.add_new_car_with_owner(data)
    return new_car


@router.get(
    "/count",
    status_code=status.HTTP_200_OK,
    response_model=dict[str, int],
    summary="Получить общее количество автомобилей в БД",
    dependencies=[Depends(allow_management)],
)
async def get_count_cars(session: SessionDep):
    service = CarService(session)
    car_count = await service.get_count_cars()
    return {"count": car_count}


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=List[CarResponseSchema],
    summary="Получить список автомобилей с фильтрацией",
    dependencies=[Depends(allow_management)],
)
async def search_cars(
    session: SessionDep,
    params: CarSearchQueryParams = Depends(),
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
    "/{car_id}",
    status_code=status.HTTP_200_OK,
    response_model=CarResponseSchema,
    summary="Получить автомобиль по ID с владельцем",
)
async def get_car_by_id_with_owners(
    car_id: str,
    current_user: CurrentUser,
    session: SessionDep,
):
    service = CarService(session)
    car = await service.get_car_by_id_with_owners(car_id)
    # Если запрос отправляет не владелец авто или не менеджер, то выбросит ошибку
    check_car_owner_or_manager(car, current_user)
    return car


@router.patch(
    "/{car_id}",
    status_code=status.HTTP_200_OK,
    response_model=CarResponseSchema,
    summary="Обновление данных об автомобиле или сменить/добавить владельца",
)
async def update_car(
    car_id: str, data: CarUpdateSchema, current_user: CurrentUser, session: SessionDep
):
    service = CarService(session)
    car = await service.update_car(car_id=car_id, data=data)
    check_car_owner_or_manager(car, current_user)
    return car


CarResponseSchema.model_rebuild()
