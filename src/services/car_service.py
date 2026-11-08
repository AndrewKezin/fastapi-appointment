from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from src.models.cars import CarModel
from src.models.ownership import UserCarOwnership

from src.repositories.car_repo import CarRepository

from src.schemas.cars import CarCreateSchema, CarResponseSchema
from src.schemas.users import UserMinResponseSchema


class CarService:
    def __init__(self, session: AsyncSession):
        self.repo = CarRepository(session)

    async def add_new_car_with_owner(self, data: CarCreateSchema) -> CarResponseSchema:
        # проверяем уникальность vin
        non_unique_vin = await self.repo.get_car_by_vin(data.vin_number)

        if non_unique_vin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Автомобиль с таким vin-номером {data.vin_number} уже зарегистрирован",
            )

        # выделить id пользователя и перевести данные схемы в чистый словарь
        car_data = data.model_dump()
        owner_id = car_data.pop(
            "owner_id"
        )  # извлечь owner_id, т.к. в таблице cars его нет

        # отправить данные в репозиторий
        new_car = await self.repo.create_car(car_data, owner_id)

        # Если репозиторий вернул None, значит запрос упал
        if not new_car:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Не удалось создать запись в базе данных. Проверьте правильность вводимых данных.",
            )

        return CarResponseSchema.model_validate(new_car)

    async def get_all_cars_with_owners(self) -> List[CarResponseSchema]:
        cars = await self.repo.get_all_cars_with_owners()

        if len(cars) == 0:
            raise HTTPException(status_code=404, detail="Автомобили не найдены")

        return [CarResponseSchema.model_validate(car) for car in cars]

    async def get_count_cars(self) -> int:
        cars_count = await self.repo.count(CarModel)

        if cars_count == 0:
            raise HTTPException(status_code=404, detail="Автомобили не найдены")

        return cars_count

    async def get_car_by_id_with_owners(
        self, car_id: str
    ) -> Optional[CarResponseSchema]:
        car = await self.repo.get_car_by_id_with_owners(car_id)

        if not car:
            raise HTTPException(status_code=404, detail="Автомобиль не найден")

        return CarResponseSchema.model_validate(car)

    async def get_car_by_vin_with_owners(
        self, vin_number: str
    ) -> Optional[CarResponseSchema]:
        car = await self.repo.get_car_by_vin_with_owners(vin_number)

        if not car:
            raise HTTPException(status_code=404, detail="Автомобиль не найден")

        return CarResponseSchema.model_validate(car)

    async def get_car_by_reg_number_with_owners(
        self, reg_number: str
    ) -> Optional[CarResponseSchema]:
        car = await self.repo.get_car_by_reg_number_with_owners(reg_number)

        if not car:
            raise HTTPException(status_code=404, detail="Автомобиль не найден")

        return CarResponseSchema.model_validate(car)


CarResponseSchema.model_rebuild()
