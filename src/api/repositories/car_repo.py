from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.repositories.base_repo import BaseRepository
from src.models.cars import CarModel
from src.schemas.cars import SCarAdd

class CarRepository(BaseRepository[CarModel]):
    def __init__(self):
        super().__init__(CarModel)

    async def create_car(self, session: AsyncSession, data: SCarAdd) -> CarModel:
        pass


    async def find_by_vin(self, session: AsyncSession, vin: str) -> CarModel | None:
        result = await session.execute(select(CarModel).where(func.lower(CarModel.vin_number) == vin.lower()))
        return result.scalar_one_or_none()

    async def find_by_reg_number(self, session: AsyncSession, reg_number: str) -> CarModel | None:
        result = await session.execute(select(CarModel).where(func.lower(CarModel.reg_number) == reg_number.lower()))
        return result.scalar_one_or_none()

    