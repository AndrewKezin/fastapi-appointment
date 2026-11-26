from typing import Annotated
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.auth.deps import RoleChecker
from src.models.users import UserModel
from src.schemas.users import UserRoleEnum

SessionDep = Annotated[AsyncSession, Depends(get_session)]

forbidden_exc = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN, detail="Недстаточно прав для доступа"
)

# Зависимость только для администраторов
allow_admin_only = RoleChecker([UserRoleEnum.ADMIN])


def check_owner_or_admin(user_id: str, current_user: UserModel) -> None:
    """Проверяет, что запрос делает сам владелец аккаунта или админ"""
    if current_user.id != user_id and current_user.role != UserRoleEnum.ADMIN:
        raise forbidden_exc
