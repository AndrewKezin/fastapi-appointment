from datetime import datetime, timezone, timedelta

import bcrypt
import jwt
from src.config import settings

TOKEN_TYPE_FIELD = "type"
ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"


# хэшировать пароль
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode(
        "utf-8"
    )  # в моей БД пароль - String(255)


# сверить пароль
def check_password(password: str, hashed_password: str | bytes) -> bool:
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password)


def create_jwt(
    token_type: str,
    token_data: dict,
    expire_minutes: int = settings.auth_jwt.access_token_expire_minutes,
    expire_timedelta: timedelta | None = None,
) -> str:
    jwt_payload = {TOKEN_TYPE_FIELD: token_type}
    jwt_payload.update(token_data)

    now = datetime.now(timezone.utc)
    if expire_timedelta:
        expire = now + expire_timedelta
    else:
        expire = now + timedelta(minutes=expire_minutes)

    jwt_payload.update(exp=expire, iat=now)

    return jwt.encode(
        jwt_payload,
        settings.auth_jwt.private_key_path.read_text(),
        algorithm=settings.auth_jwt.algorithm,
    )


def create_access_token(
    user_id: str,
    email: str,
    role: str,
) -> str:
    payload = {
        "sub": user_id,
        "email": email,
        "role": role,
    }

    return create_jwt(
        token_type=ACCESS_TOKEN_TYPE,
        token_data=payload,
        expire_minutes=settings.auth_jwt.access_token_expire_minutes,
    )


def create_refresh_token(user_id: str) -> str:
    payload = {
        "sub": user_id,
    }

    return create_jwt(
        token_type=REFRESH_TOKEN_TYPE,
        token_data=payload,
        expire_timedelta=timedelta(days=settings.auth_jwt.refresh_token_expire_days),
    )


def decode_token(
    token: str | bytes,
    public_key: str = settings.auth_jwt.public_key_path.read_text(),
    algorithm: str = settings.auth_jwt.algorithm,
):
    return jwt.decode(token, public_key, algorithms=[algorithm])
