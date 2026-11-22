from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.models.users import UserModel
from src.auth.security import check_password, decode_token

# tokenUrl должен совпадать с полным путем до эндпоинта логина
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# Проверяем email и пароль при входе (через стандартную форму OAuth2PasswordRequestForm, чтобы работала кнопка Authorize в Swagger).
async def validate_auth_user(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UserModel:
    # В OAuth2PasswordRequestForm поле логина всегда называется username, передаем туда email
    stmt = select(UserModel).where(UserModel.email == form_data.username)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    unauthed_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Неверный email или пароль",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not user or not check_password(form_data.password, user.hashed_password):
        raise unauthed_exc

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Аккаунт пользователя деактивирован",
        )

    return user

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UserModel:
    creds_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Невалидный токен авторизации",
        headers={"WWW-Authenticate": "Bearer"},
    )
    # Достаем токен из заголовка и проверяем его публичным ключом
    try:
        payload = decode_token(token)
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise creds_exception
    except jwt.InvalidTokenError:
        raise creds_exception

    # Находим пользователя в БД
    stmt = select(UserModel).where(UserModel.id == user_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        raise creds_exception

    return user

# Проверяем, что пользователь активен (не заблокирован)
async def get_current_active_user(
    current_user: Annotated[UserModel, Depends(get_session)]
) -> UserModel:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Аккаунт пользователя деактивирован",
        )
    return current_user