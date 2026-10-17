from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.schemas.users import UserCreateSchema
from src.services.user_service import UserService

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.post("/")
async def create_user(data: UserCreateSchema, session: AsyncSession = Depends(get_session)):
    service = UserService(session)
    user = await service.create_user(data)
    return {"data": user}

@router.get("/")
async def get_all_users(session: AsyncSession = Depends(get_session)):
    service = UserService(session)
    users = await service.get_all_users()
    return {"data": users}

# Статические пути всегда должны идти до динамических путей с переменными!
@router.get("/count")
async def get_count_users(session: AsyncSession = Depends(get_session)):
    service = UserService(session)
    count = await service.get_count_users()
    return {"data": count}

@router.get("/{user_id}")
async def get_user_by_id(user_id: str, session: AsyncSession = Depends(get_session)):
    service = UserService(session)
    user = await service.get_user_by_id(user_id)
    return {"data": user}

@router.get("/lastname/{last_name}")
async def get_users_by_last_name(last_name: str, session: AsyncSession = Depends(get_session)):
    service = UserService(session)
    users = await service.get_users_by_last_name(last_name)
    return {"data": users}

@router.delete("/{user_id}", summary="Удаление данных о пользователе (id и хеш пароля сохраняются)")
async def soft_delete_user(user_id: str, session: AsyncSession = Depends(get_session)):
    service = UserService(session)
    user = await service.soft_delete_user(user_id)
    return {"data": user}

# @router.post("/register")

# @router.post("/login")