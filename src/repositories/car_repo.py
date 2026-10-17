from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.base_repo import BaseRepository
from src.models.cars import CarModel
from src.schemas.cars import CarBaseSchema

class CarRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def create_car(self, data: CarBaseSchema) -> CarModel:
        car = CarModel(**data.model_dump())
        self.session.add(car)
        await self.session.commit()
        await self.session.refresh(car)
        return car


    async def get_car_by_vin(self, vin_number: str) -> Optional[CarModel]:
        result = await self.session.execute(select(CarModel).where(func.lower(CarModel.vin_number) == vin_number.lower()))
        return result.scalar_one_or_none()

    async def get_car_by_reg_number(self, reg_number: str) -> Optional[CarModel]:
        result = await self.session.execute(select(CarModel).where(func.lower(CarModel.reg_number) == reg_number.lower()))
        return result.scalar_one_or_none()
    

    