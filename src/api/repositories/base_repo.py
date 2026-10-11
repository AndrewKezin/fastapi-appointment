from typing import Generic, TypeVar, Optional
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T", bound=DeclarativeBase)

class BaseRepository(Generic[T]):
    def __init__(self, model: type[T]):
        self.model = model

    async def get_by_id(self, session: AsyncSession, id_: str) -> Optional[T]:
        result = await session.execute(select(self.model).where(self.model.id == id_))
        return result.scalar_one_or_none()

    async def get_all(self, session: AsyncSession) -> list[T]:
        result = await session.execute(select(self.model))
        return list(result.scalars().all())