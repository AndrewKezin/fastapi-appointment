from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.base_repo import BaseRepository
from src.models.users import UserModel


class UserRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def create_user(self, data: dict) -> UserModel:
        """
        Создаёт пользователя и возвращает ORM-модель.
        Конвертацию в UserResponseSchema делает сервис или API.
        """
        user = UserModel(**data)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    # async def change_role_user(self, user_id: str, data: UserChangeRoleSchema) -> Optional[UserModel]:
    #     user = await self.session.execute(select(UserModel).where(UserModel.id == user_id)).scalar_one_or_none()
    #     user.role = data.role
    #     await self.session.commit()
    #     return user

    async def get_user_by_id(self, user_id: str) -> Optional[UserModel]:
        return await super().get_by_id(UserModel, user_id)

    async def get_user_by_email(self, email: str) -> Optional[UserModel]:
        result = await self.session.execute(select(UserModel).where(UserModel.email == email))  
        return result.scalar_one_or_none()

    async def get_users_by_last_name(self, last_name: str) -> List[UserModel]:
        # Создаем шаблон вида '%иванов%'
        search_pattern = f"%{last_name}%"

        stmt = select(UserModel).where(UserModel.last_name.ilike(search_pattern)) # ilike - не чувствителен к регистру
        result = await self.session.execute(stmt)
        
        return list(result.scalars().all())


    async def get_count_users(self) -> int:
        return await super().count(UserModel)

    async def soft_delete_user(self, user_id: str) -> Optional[UserModel]:
        result: UserModel = await self.session.execute(select(UserModel).where(UserModel.id == user_id))
        user = result.scalar_one_or_none()
        user.is_active = False
        user.first_name = "DELETED"
        user.middle_name = None
        user.last_name = "DELETED"
        user.address = "ADDRESS DELETED"
        user.phone = "PHONE DELETED"
        await self.session.commit()
        await self.session.refresh(user)
        return user

    

    