from typing import Annotated
from fastapi import APIRouter, Depends

from src.models.users import UserModel
from src.schemas.auth import TokenInfo
from src.auth.security import create_access_token
from src.auth.deps import validate_auth_user, get_current_active_user

router = APIRouter(prefix="/auth", tags=["Auth"])


# Эндпоинт для выдачи токена
@router.post("/login", response_model=TokenInfo)
async def login_for_access_token(
    user: Annotated[UserModel, Depends(validate_auth_user)],
):
    jwt_payload = {"sub": user.id, "email": user.email, "role": user.role.value}
    access_token = create_access_token(jwt_payload)
    return TokenInfo(access_token=access_token)


# Тестовый маршрут
@router.post("/me")
async def get_my_profile(
    current_user=Annotated[UserModel, Depends(get_current_active_user)],
):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "first_name": current_user.first_name,
        "role": current_user.role,
    }
