from typing import Annotated, List

from fastapi import APIRouter, Depends, status

from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.deps import get_current_active_user
from src.database import get_session
from src.models.users import UserModel
from src.schemas.users import (
    UserCreateSchema,
    UserResponseSchema,
    UserRoleEnum,
    UserWithCarsResponseSchema,
    UserSearchQueryParams,
    UserUpdateSchema,
)
from src.schemas.cars import CarByUserResponseSchema
from src.services.user_service import UserService
from src.api.dependencies import allow_admin_only, check_owner_or_admin, forbidden_exc

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponseSchema,
    summary="Добавление нового пользователя",
)
async def create_user(
    data: UserCreateSchema, session: AsyncSession = Depends(get_session)
):
    service = UserService(session)
    user = await service.create_user(data)

    return user


# Не используется, т.к. роут get_all_users заменяет роут search_users
# @router.get(
#     "/",
#     status_code=status.HTTP_200_OK,
#     response_model=List[UserResponseSchema],
#     summary="Получить список пользователей",
# )
# async def get_all_users(session: AsyncSession = Depends(get_session)):

#     service = UserService(session)
#     users = await service.get_all_users()

#     return users


@router.get(
    "/count",
    status_code=status.HTTP_200_OK,
    response_model=dict[str, int],
    summary="Получить общее количество пользователей в БД",
    dependencies=[Depends(allow_admin_only)],  # Только для админа
)
async def get_count_users(session: AsyncSession = Depends(get_session)):
    service = UserService(session)
    count = await service.get_count_users()

    return {"count": count}


@router.get(
    "/search",
    status_code=status.HTTP_200_OK,
    response_model=List[UserResponseSchema],
    summary="Получить список пользователей с фильтрацией",
    dependencies=[Depends(allow_admin_only)],
)
async def search_users(
    params: UserSearchQueryParams = Depends(),
    session: AsyncSession = Depends(get_session),
):
    service = UserService(session)

    users = await service.search_users(
        email=params.email,
        first_name=params.first_name,
        middle_name=params.middle_name,
        last_name=params.last_name,
        phone=params.phone,
        address=params.address,
        limit=params.limit,
        offset=params.offset,
    )

    return users


# Статические пути всегда должны идти до динамических путей с переменными.
@router.get(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=UserWithCarsResponseSchema,
    summary="Получить пользователя по ID",
)
async def get_user_by_id_with_cars(
    user_id: str,
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    session: AsyncSession = Depends(get_session),
):
    # Роут доступен самому пользователю и админу. Если проверка не пройдет, то выкинет ошибку.
    check_owner_or_admin(user_id, current_user)

    service = UserService(session)
    user = await service.get_user_by_id_with_cars(user_id)

    return user


@router.patch(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=UserResponseSchema,
    summary="Обновление данных о пользователе",
)
async def update_user(
    user_id: str,
    data: UserUpdateSchema,
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    session: AsyncSession = Depends(get_session),
):
    check_owner_or_admin(user_id, current_user)  # только пользователь и админ

    # Защита от привелегий: обычный пользователь не может менять свою роль или статус активности
    if current_user.role != UserRoleEnum.ADMIN:
        if (
            getattr(data, "role", None) is not None
            or getattr(data, "is_active", None) is not None
        ):
            raise forbidden_exc

    service = UserService(session)

    return await service.update_user(user_id=user_id, data=data)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=UserResponseSchema,
    summary="Удаление персональных данных о пользователе (id, хеш пароля и привязка к автомобилям сохраняются)",
)
async def soft_delete_user(
    user_id: str,
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    session: AsyncSession = Depends(get_session),
):
    check_owner_or_admin(user_id, current_user)  # только пользователь и админ

    service = UserService(session)
    user = await service.soft_delete_user(user_id)

    return user


UserWithCarsResponseSchema.model_rebuild()
