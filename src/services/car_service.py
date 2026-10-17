from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from src.models.cars import CarModel
from src.repositories.car_repo import CarRepository
from src.schemas.cars import CarBaseSchema, CarResponseSchema


class CarService:
    def __init__(self, session: AsyncSession):
        self.repo = CarRepository(session)

    async def add_car(self, data: CarBaseSchema) -> CarResponseSchema:
        # проверяем уникальность vin
        non_unique_vin = await self.repo.get_car_by_vin(data.vin_number)
        if non_unique_vin:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Автомобиль с таким vin-номером {data.vin_number} уже зарегистрирован")

        new_car = await self.repo.create_car(data)

        return CarResponseSchema.model_validate(new_car)

    async def get_all_cars(self) -> List[CarResponseSchema]:
        cars = await self.repo.get_all(CarModel)

        if len(cars) == 0:
            raise HTTPException(status_code=404, detail="Автомобили не найдены")
        
        return [CarResponseSchema.model_validate(car) for car in cars]

    async def get_count_cars(self) -> int:
        cars_count = await self.repo.count(CarModel)

        if cars_count == 0:
            raise HTTPException(status_code=404, detail="Автомобили не найдены")
        
        return cars_count

    async def get_car_by_id(self, car_id: str) -> Optional[CarResponseSchema]:
        car = await self.repo.get_by_id(CarModel, car_id)

        if not car:
            raise HTTPException(status_code=404, detail="Автомобиль не найден")

        return CarResponseSchema.model_validate(car)

    async def get_car_by_vin(self, vin_number: str) -> Optional[CarResponseSchema]:
        car = await self.repo.get_car_by_vin(vin_number)

        if not car:
            raise HTTPException(status_code=404, detail="Автомобиль не найден")

        return CarResponseSchema.model_validate(car)

    async def get_car_by_reg_number(self, reg_number: str) -> Optional[CarResponseSchema]:
        car = await self.repo.get_car_by_reg_number(reg_number)

        if not car:
            raise HTTPException(status_code=404, detail="Автомобиль не найден")

        return CarResponseSchema.model_validate(car)