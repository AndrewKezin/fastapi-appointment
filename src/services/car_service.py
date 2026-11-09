from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from src.models.cars import CarModel
from src.repositories.car_repo import CarRepository
from src.schemas.cars import CarCreateSchema


class CarService:
    def __init__(self, session: AsyncSession):
        self.repo = CarRepository(session)

    async def add_new_car_with_owner(self, data: CarCreateSchema) -> CarModel:
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

        return new_car

    async def get_all_cars_with_owners(self) -> List[CarModel]:
        return await self.repo.get_all_cars_with_owners()

    async def get_count_cars(self) -> int:
        return await self.repo.count(CarModel)

    async def get_car_by_id_with_owners(self, car_id: str) -> CarModel:
        car = await self.repo.get_car_by_id_with_owners(car_id)

        if not car:
            raise HTTPException(status_code=404, detail="Автомобиль не найден")

        return car

    async def search_cars(
        self,
        vin_number: str | None,
        reg_number: str | None,
        brand: str | None,
        model: str | None,
        limit: int,
        offset: int,
    ) -> List[CarModel]:
        """Сервисный метод для поиска автомобилей по фильтрам."""
        cars = await self.repo.get_car_by_query_params(
            vin_number=vin_number,
            reg_number=reg_number,
            brand=brand,
            model=model,
            limit=limit,
            offset=offset,
        )

        """если ничего не найдено, стандарт и правильное поведение REST API - статус `200 OK` с пустым массивом. 
        Бросать ошибку `404` стоит только при поиске конкретного элемента по его уникальному ID"""

        """если у эндпоинта в роутере прописан параметр response_model=List[UserResponseSchema], 
        то делать ручной model_validate в цикле не нужно. 
        FastAPI сделает это автоматически на выходе из роутера"""
        return cars
