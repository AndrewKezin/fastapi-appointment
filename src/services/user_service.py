from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from src.models.users import UserModel
from src.repositories.user_repo import UserRepository
from src.schemas.users import UserCreateSchema, UserChangeRoleSchema, UserResponseSchema
from src.auth.security import hash_password


class UserService:
    def __init__(self, session: AsyncSession):
        self.repo = UserRepository(session)

    async def create_user(self, data: UserCreateSchema) -> UserResponseSchema:
        # проверяем уникальность email
        non_unique_email = await self.repo.get_user_by_email(data.email)
        if non_unique_email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Пользователь с таким email {data.email} уже зарегистрирован")

        # хешируем пароль
        hashed_password = hash_password(data.password)

        # Создаём dict без пароля, потом добавляем хешированный пароль
        user_data = data.model_dump(exclude={"password"})
        user_data["hashed_password"] = hashed_password

        user = await self.repo.create_user(user_data)

        # возвращаем Pydantic-схему (без пароля)
        return UserResponseSchema.model_validate(user)

    async def change_role_user(self, user_id: str, data: UserChangeRoleSchema) -> UserResponseSchema:
        user = await self.repo.change_role_user(user_id, data)
        return UserResponseSchema.model_validate(user)
    
    async def get_user_by_id(self, user_id: str) -> Optional[UserResponseSchema]:
        result = await self.repo.get_user_by_id(user_id)

        if not result:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
    
        return UserResponseSchema.model_validate(result)

    # async def get_user_by_email(self, email: str) -> Optional[UserResponseSchema]:
    #     result = await self.repo.get_user_by_email(email)
    #     return UserResponseSchema.model_validate(result)

    async def get_all_users(self) -> List[UserResponseSchema]:
        result = await self.repo.get_all(UserModel) # обратиться к базовому репозиторию

        if len(result) == 0:
            raise HTTPException(status_code=404, detail="Пользователи не найдены")
        
        return [UserResponseSchema.model_validate(user) for user in result]

    async def get_count_users(self) -> int:
        user_count = await self.repo.count(UserModel)

        if user_count == 0:
            raise HTTPException(status_code=404, detail="Пользователи не найдены")
        
        return user_count

    async def get_users_by_last_name(self, last_name: str) -> List[UserResponseSchema]:
        result = await self.repo.get_users_by_last_name(last_name)

        if len(result) == 0:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        
        return [UserResponseSchema.model_validate(user) for user in result]

    async def soft_delete_user(self, user_id: str) -> Optional[UserResponseSchema]:
        user = await self.repo.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        if user.is_active == False:
            raise HTTPException(status_code=400, detail="Пользователь уже удалён")
        
        result = await self.repo.soft_delete_user(user_id)

        return UserResponseSchema.model_validate(result)
    