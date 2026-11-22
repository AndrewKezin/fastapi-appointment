from datetime import datetime, timezone, timedelta

import bcrypt
import jwt
from src.config import settings

 
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8") # в моей БД пароль - String(255)


def check_password(password: str, hashed_password: str | bytes) -> bool:
    if isinstance (hashed_password, str):
        hashed_password = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password)


# добавить JWT
def create_access_token(
    payload: dict,
    private_key: str = settings.auth_jwt.private_key_path.read_text(),
    algorithm: str = settings.auth_jwt.algorithm,
    expire_minutes: int = settings.auth_jwt.access_token_expire_minutes,
):
    to_encode = payload.copy()
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=expire_minutes)

    to_encode.update(exp=expire, iat=now)

    return jwt.encode(to_encode, private_key, algorithm=algorithm)


def decode_token(
    token: str | bytes,
    public_key: str = settings.auth_jwt.public_key_path.read_text(),
    algorithm: str = settings.auth_jwt.algorithm,
):
    return jwt.decode(token, public_key, algorithms=[algorithm])
