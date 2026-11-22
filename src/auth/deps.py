from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.models.users import UserModel
from src.schemas.users import UserRoleEnum
from src.auth.security import (
    check_password,
    decode_token,
    TOKEN_TYPE_FIELD,
    ACCESS_TOKEN_TYPE,
    REFRESH_TOKEN_TYPE,
)

# tokenUrl должен совпадать с полным путем до эндпоинта логина
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def _get_user_by_token_type(
    token: str,
    expected_token_type: str,
    session: AsyncSession,
) -> UserModel:
    creds_exceptions = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Невалидный токен авторизации",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        token_type = payload.get(TOKEN_TYPE_FIELD)
        if token_type != expected_token_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Неверный тип токена: ожидался '{expected_token_type}'",
            )

        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise creds_exceptions

    except jwt.InvalidTokenError as e:
        print(f"Ошибка проверки JWT: {type(e).__name__} — {e}")
        raise creds_exceptions

    stmt = select(UserModel).where(UserModel.id == user_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        raise creds_exceptions
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Аккаунт пользователя заблокирован",
        )

    return user


# Зависимость для обычных защищенных эндпоинтов (проверяет ACCESS токен)
async def get_current_active_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UserModel:
    return await _get_user_by_token_type(token, ACCESS_TOKEN_TYPE, session)


# Зависимость специально для эндпоинта обновления токена (проверяет REFRESH токен)
async def get_current_user_for_refresh(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UserModel:
    return await _get_user_by_token_type(token, REFRESH_TOKEN_TYPE, session)


async def validate_auth_user(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UserModel:
    # В стандартной форме OAuth2 логин всегда передается в поле username — ищем по нему email
    stmt = select(UserModel).where(UserModel.email == form_data.username)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    unauthed_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Неверный email или пароль",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if user is None or not check_password(form_data.password, user.hashed_password):
        raise unauthed_exc

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Пользователь деактивирован",
        )

    return user


# Класс-фабрика для проверки ролей
class RoleChecker:
    def __init__(self, allowed_roles: list[UserRoleEnum]):
        self.allowed_roles = allowed_roles

    def __call__(
        self,
        user: Annotated[UserModel, Depends(get_current_active_user)],
    ) -> UserModel:
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав для выполнения этого действия",
            )
        return user
