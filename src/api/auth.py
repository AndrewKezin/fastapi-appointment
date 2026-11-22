from typing import Annotated
from fastapi import APIRouter, Depends

from src.models.users import UserModel
from src.schemas.auth import TokenInfo
from src.auth.security import create_access_token, create_refresh_token
from src.auth.deps import (
    validate_auth_user,
    get_current_active_user,
    get_current_user_for_refresh,
)
from src.schemas.users import UserProfileResponse, UserResponseSchema

router = APIRouter(prefix="/auth", tags=["Auth"])

"""
    При входе пользователь получает сразу два токена, 
    а когда access_token истечёт через 15 минут, 
    фронтенд сможет отправить refresh_token в заголовок Authorization: Bearer <refresh_token> 
    на эндпоинт /auth/refresh и получить новую пару
"""


# Эндпоинт для выдачи токенов
@router.post("/login", response_model=TokenInfo)
async def login_for_access_token(
    user: Annotated[UserModel, Depends(validate_auth_user)],
):
    access_token = create_access_token(user.id, user.email, user.role.value)
    refresh_token = create_refresh_token(user.id)
    return TokenInfo(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/refresh", response_model=TokenInfo)
async def refresh_jwt(
    user: Annotated[UserModel, Depends(get_current_user_for_refresh)],
):
    # новая пара токенов (Token Rotation)
    access_token = create_access_token(user.id, user.email, user.role.value)
    refresh_token = create_refresh_token(user.id)
    return TokenInfo(
        access_token=access_token,
        refresh_token=refresh_token,
    )


# Тестовый маршрут
@router.post("/me", response_model=UserResponseSchema)
async def get_my_profile(
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
):
    return current_user
