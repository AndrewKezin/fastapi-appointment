from typing import List

from fastapi import APIRouter, Depends, status

from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.schemas.users import UserCreateSchema, UserResponseSchema, UserWithCarsResponseSchema
from src.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=UserResponseSchema
)
async def create_user(
    data: UserCreateSchema, session: AsyncSession = Depends(get_session)
):
    service = UserService(session)
    user = await service.create_user(data)

    return user


@router.get("/", status_code=status.HTTP_200_OK, response_model=List[UserResponseSchema])
async def get_all_users(session: AsyncSession = Depends(get_session)):
    service = UserService(session)
    users = await service.get_all_users()

    return users


# Статические пути всегда должны идти до динамических путей с переменными!
@router.get("/count")
async def get_count_users(session: AsyncSession = Depends(get_session)):
    service = UserService(session)
    count = await service.get_count_users()

    return {"count": count}


@router.get("/{user_id}", status_code=status.HTTP_200_OK, response_model=UserWithCarsResponseSchema)
async def get_user_by_id_with_cars(
    user_id: str, session: AsyncSession = Depends(get_session)
):
    service = UserService(session)
    user = await service.get_user_by_id_with_cars(user_id)
    
    return user


@router.get("/lastname/{last_name}")
async def get_users_by_last_name(
    last_name: str, session: AsyncSession = Depends(get_session)
):
    service = UserService(session)
    users = await service.get_users_by_last_name(last_name)

    return {"data": users}


@router.delete(
    "/{user_id}", summary="Удаление данных о пользователе (id и хеш пароля сохраняются)"
)
async def soft_delete_user(user_id: str, session: AsyncSession = Depends(get_session)):
    service = UserService(session)
    user = await service.soft_delete_user(user_id)

    return {"data": user}


# @router.post("/register")

# @router.post("/login")
