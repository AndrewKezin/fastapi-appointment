from typing import Any, List, Type, Optional
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self, model: Type[Any]) -> List[Any]:
        result = await self.session.execute(select(model))
        return result.scalars().all()

    async def get_by_id(self, model: Type[Any], id_: str) -> Optional[Any]:
        result = await self.session.execute(select(model).where(model.id == id_))
        return result.scalar_one_or_none()

    async def count(self, model: Type[Any]) -> int:
        result = await self.session.execute(select(func.count()).select_from(model))
        return result.scalar() or 0
