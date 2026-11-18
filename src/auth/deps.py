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
