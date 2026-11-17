from typing import List

from fastapi import APIRouter, Depends, status

from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.schemas.users import (
    UserCreateSchema,
    UserResponseSchema,
    UserWithCarsResponseSchema,
    UserSearchQueryParams,
    UserUpdateSchema,
)
from src.schemas.cars import CarByUserResponseSchema
from src.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponseSchema,
    summary="Добавление нового пользователя",
)
async def create_user(
    data: UserCreateSchema, session: AsyncSession = Depends(get_session)
):
    service = UserService(session)
    user = await service.create_user(data)

    return user


# Не используется, т.к. роут get_all_users заменяет роут search_users
# @router.get(
#     "/",
#     status_code=status.HTTP_200_OK,
#     response_model=List[UserResponseSchema],
#     summary="Получить список пользователей",
# )
# async def get_all_users(session: AsyncSession = Depends(get_session)):

#     service = UserService(session)
#     users = await service.get_all_users()

#     return users


# Статические пути всегда должны идти до динамических путей с переменными!
@router.get(
    "/count",
    status_code=status.HTTP_200_OK,
    response_model=dict[str, int],
    summary="Получить общее количество пользователей в БД",
)
async def get_count_users(session: AsyncSession = Depends(get_session)):
    service = UserService(session)
    count = await service.get_count_users()

    return {"count": count}


@router.get(
    "/search",
    status_code=status.HTTP_200_OK,
    response_model=List[UserResponseSchema],
    summary="Получить список пользователей с фильтрацией",
)
async def search_users(
    params: UserSearchQueryParams = Depends(),
    session: AsyncSession = Depends(get_session),
):
    service = UserService(session)

    users = await service.search_users(
        email=params.email,
        first_name=params.first_name,
        middle_name=params.middle_name,
        last_name=params.last_name,
        phone=params.phone,
        address=params.address,
        limit=params.limit,
        offset=params.offset,
    )

    return users


@router.get(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=UserWithCarsResponseSchema,
    summary="Получить пользователя по ID",
)
async def get_user_by_id_with_cars(
    user_id: str, session: AsyncSession = Depends(get_session)
):
    service = UserService(session)
    user = await service.get_user_by_id_with_cars(user_id)

    return user


@router.patch(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=UserResponseSchema,
    summary="Обновление данных о пользователе",
)
async def update_user(
    user_id: str, data: UserUpdateSchema, session: AsyncSession = Depends(get_session)
):
    service = UserService(session)

    return await service.update_user(user_id=user_id, data=data)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=UserResponseSchema,
    summary="Удаление персональных данных о пользователе (id, хеш пароля и привязка к автомобилям сохраняются)",
)
async def soft_delete_user(user_id: str, session: AsyncSession = Depends(get_session)):
    service = UserService(session)
    user = await service.soft_delete_user(user_id)

    return user


UserWithCarsResponseSchema.model_rebuild()
