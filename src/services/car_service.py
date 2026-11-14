from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from src.models.cars import CarModel
from src.repositories.car_repo import CarRepository
from src.schemas.cars import CarCreateSchema, CarUpdateSchema


class CarService:
    def __init__(self, session: AsyncSession):
        self.repo = CarRepository(session)

    async def add_new_car_with_owner(self, data: CarCreateSchema) -> CarModel:
        # проверяем уникальность vin
        non_unique_vin = await self.repo.get_car_by_vin(data.vin_number)

        if non_unique_vin:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Автомобиль с таким vin-номером {data.vin_number} уже зарегистрирован",
            )

        # выделить id пользователя и перевести данные схемы в чистый словарь
        car_data = data.model_dump()
        # извлечь owner_id, т.к. в таблице cars его нет
        owner_id = car_data.pop("owner_id")

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
        то делать ручной model_validate в сервисном слое не обязательно. 
        FastAPI сделает это автоматически на выходе из роутера"""
        return cars

    async def update_car(self, car_id: str, data: CarUpdateSchema) -> CarModel:
        # Проверка на существование автомобиля
        car: Optional[CarModel] = await self.repo.get_car_by_id_with_owners(car_id)
        if not car:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Автомобиль с id: {car_id} не найден",
            )

        # Берем только заполненные поля
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return car

        # Безопасно извлекаем поля владельца (с дефолтными значениями, чтобы избежать KeyError)
        owner_id = update_data.pop("owner_id", None)
        is_primary_owner = update_data.pop("is_primary_owner", True)

        # проверка измененного vin-номера на уникальность
        if "vin_number" in update_data and update_data["vin_number"] != car.vin_number:
            existing_vin = await self.repo.get_car_by_vin(update_data["vin-number"])
            if existing_vin:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Автомобиль с VIN-номером {update_data['vin-number']} уже зарегистрирован с базе данных",
                )

        # Проверка уникальности госномера, если он изменяется
        if "reg_number" in update_data and update_data["reg_number"] != car.reg_number:
            existing_reg = await self.repo.get_car_by_reg_number(
                update_data["reg_number"]
            )
            if existing_reg:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Автомобиль с таким госномером уже существует",
                )

        # отправить данные в репозиторий
        updated_car = await self.repo.update_car(
            car=car,
            update_data=update_data,
            owner_id=owner_id,
            is_primary_owner=is_primary_owner,
        )

        # Если репозиторий вернул None, значит запрос упал
        if not updated_car:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Не удалось изменить запись в базе данных. Проверьте правильность вводимых данных.",
            )

        return updated_car
