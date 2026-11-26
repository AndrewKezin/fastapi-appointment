from typing import Annotated
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.auth.deps import RoleChecker, get_current_active_user
from src.models.cars import CarModel
from src.models.users import UserModel
from src.schemas.users import UserRoleEnum

SessionDep = Annotated[AsyncSession, Depends(get_session)]

CurrentUser = Annotated[UserModel, Depends(get_current_active_user)]

forbidden_exc = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN, detail="Недостаточно прав для доступа"
)

# Зависимости
# Только для администраторов
allow_admin_only = RoleChecker([UserRoleEnum.ADMIN])

# Руководство и приемка
allow_management = RoleChecker(
    [
        UserRoleEnum.ADMIN,
        UserRoleEnum.MANAGER,
    ]
)

# Весь персонал техцентра
allow_staff = RoleChecker(
    [
        UserRoleEnum.ADMIN,
        UserRoleEnum.MANAGER,
        UserRoleEnum.MECHANIC,
    ]
)

# Только исполнители ремонта
allow_mechanics = RoleChecker(
    [
        UserRoleEnum.ADMIN,
        UserRoleEnum.MECHANIC,
    ]
)


def check_owner_or_admin(user_id: str, current_user: UserModel) -> None:
    """Проверяет, что запрос делает сам владелец аккаунта или админ"""
    if current_user.id != user_id and current_user.role != UserRoleEnum.ADMIN:
        raise forbidden_exc

def check_car_owner_or_manager(car: CarModel, current_user: UserModel) -> None:
    """Проверяет, что запрос об авто делает сам владелец или менеджер техцентра"""
    is_manager = current_user.role in allow_management.allowed_roles
    is_owner = any(own.user_id == current_user.id for own in car.ownerships)
    if not is_owner and not is_manager:
        raise forbidden_exc