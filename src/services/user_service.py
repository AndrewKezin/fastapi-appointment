from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from src.models.users import UserModel
from src.repositories.user_repo import UserRepository
from src.schemas.users import UserCreateSchema, UserUpdateSchema

from src.auth.security import hash_password


class UserService:
    def __init__(self, session: AsyncSession):
        self.repo = UserRepository(session)

    async def create_user(self, data: UserCreateSchema) -> UserModel:
        # проверяем уникальность email
        non_unique_email = await self.repo.get_user_by_email(data.email)
        if non_unique_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Пользователь с таким email {data.email} уже зарегистрирован",
            )

        # хешируем пароль
        hashed_password = hash_password(data.password)

        # Создаём dict без пароля, потом добавляем хешированный пароль
        user_data = data.model_dump(exclude={"password"})
        user_data["hashed_password"] = hashed_password

        user = await self.repo.create_user(user_data)

        # возвращаем Pydantic-схему (без пароля)
        # return UserResponseSchema.model_validate(user)
        """
        если у эндпоинта в роутере прописан параметр response_model=List[UserResponseSchema], 
        то делать ручной model_validate в цикле не нужно. 
        FastAPI сделает это автоматически на выходе из роутера"""
        return user

    async def get_user_by_id_with_cars(self, user_id: str) -> UserModel:
        result = await self.repo.get_user_by_id_with_cars(user_id)

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден"
            )

        return result

    async def get_all_users(self) -> List[UserModel]:
        return await self.repo.get_all(UserModel)  # обратиться к базовому репозиторию

    async def get_count_users(self) -> int:
        return await self.repo.count(UserModel)  # обратиться к базовому репозиторию

    async def search_users(
        self,
        email: str | None,
        first_name: str | None,
        middle_name: str | None,
        last_name: str | None,
        phone: str | None,
        address: str | None,
        limit: int,
        offset: int,
    ) -> List[UserModel]:
        users = await self.repo.get_user_by_query_params(
            email=email,
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            phone=phone,
            address=address,
            limit=limit,
            offset=offset,
        )

        """если ничего не найдено, стандарт и правильное поведение REST API - статус `200 OK` с пустым массивом. 
        Бросать ошибку `404` стоит только при поиске конкретного элемента по его уникальному ID"""
        return users

    async def soft_delete_user(self, user_id: str) -> UserModel:
        user = await self.repo.get_by_id(UserModel, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден"
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь уже удалён",
            )

        result = await self.repo.soft_delete_user(user_id)

        return result

    async def update_user(self, user_id: str, data: UserUpdateSchema) -> UserModel:
        # Проверка на существование юзера
        user: Optional[UserModel] = await self.repo.get_by_id(UserModel, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден"
            )

        # Берем ТОЛЬКО те поля, которые клиент явно передал в запросе
        update_data = data.model_dump(exclude_unset=True)

        if not update_data:
            return user

        # Проверка нового email на уникальность, если он изменился
        if "email" in update_data and update_data["email"] != user.email:
            existing_user = await self.repo.get_user_by_email(update_data["email"])
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Email {update_data['email']} уже занят другим пользователем",
                )

        # Обработка смены пароля
        if "password" in update_data:
            raw_password = update_data.pop("password")
            if raw_password is not None:
                update_data["hashed_password"] = hash_password(raw_password)

        return await self.repo.update_user(user, update_data)
