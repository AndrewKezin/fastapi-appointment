from typing import List, Optional

from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload, contains_eager
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.ownership import UserCarOwnership
from src.repositories.base_repo import BaseRepository
from src.models.users import UserModel


class UserRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def create_user(self, data: dict) -> UserModel:
        user = UserModel(**data)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)

        return user

    async def get_user_by_id_with_cars(self, user_id: str) -> Optional[UserModel]:
        query = (
            select(UserModel)
            # Делаем явный JOIN с промежуточной таблицей, чтобы её поля стали доступны для ORDER BY
            .join(UserModel.ownerships)
            .where(UserModel.id == user_id)
            # Теперь сортировка по этой таблице сработает
            .order_by(desc(UserCarOwnership.ownership_start))
            .options(
                # Не делать отдельный запрос для ownerships, а «впитать» (eager load) данные из уже сделанного выше JOIN'а
                contains_eager(UserModel.ownerships)
                # А для самих машин внутри связи используем selectinload
                .selectinload(UserCarOwnership.car)
            )
        )
        result = await self.session.execute(query)
        # Так как при JOIN строк может быть несколько (по одной на каждую машину),
        # используем unique(), чтобы SQLAlchemy корректно собрала одного уникального юзера
        return result.unique().scalar_one_or_none()

    async def get_user_by_query_params(
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
        stmt = select(UserModel).options(
            selectinload(UserModel.ownerships).selectinload(UserCarOwnership.car)
        )

        # ИСПРАВИТЬ ПРОБЛЕМУ ПОИСКА ФИО С ПЕРВОЙ БУКВЫ!!!
        if email:
            stmt = stmt.where(UserModel.email.ilike(f"%{email}%"))
        if first_name:
            stmt = stmt.where(UserModel.first_name.ilike(f"%{first_name}%"))
        if middle_name:
            stmt = stmt.where(UserModel.middle_name.ilike(f"%{middle_name}%"))
        if last_name:
            stmt = stmt.where(UserModel.last_name.ilike(f"%{last_name}%"))
        if phone:
            stmt = stmt.where(UserModel.phone.ilike(f"%{phone}%"))
        if address:
            stmt = stmt.where(UserModel.address.ilike(f"%{address}%"))

        # пагинация
        stmt = stmt.limit(limit).offset(offset)

        result = await self.session.execute(stmt)

        return list(result.unique().scalars().all())

    async def soft_delete_user(self, user_id: str) -> Optional[UserModel]:
        result: UserModel = await self.session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
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
