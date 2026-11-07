from typing import List, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from src.models.ownership import UserCarOwnership
from src.repositories.base_repo import BaseRepository
from src.models.cars import CarModel


class CarRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def create_car(self, data: dict, owner_id: str) -> CarModel:
        # создать объект автомобиля через sqlalchemy
        car = CarModel(**data)
        self.session.add(car)

        try:
            # flush() отправит команду INSERT в БД и сгенерирует car.id (UUID), но транзакция останется открытой, что позволит связать таблицы
            await self.session.flush()

            # создать запись о владении в ассоциативной таблице
            ownership = UserCarOwnership(
                user_id=owner_id,
                car_id=car.id,  # передать сгенерированный выше id машины
                is_primary=True,  # назначить пользователя основным владельцем
            )
            self.session.add(ownership)

            # Фиксируем обе записи одной транзакцией
            await self.session.commit()

            query = select(CarModel).options(
                selectinload(CarModel.ownerships)
                .selectinload(UserCarOwnership.user)
            )

            result = await self.session.execute(query)
            return result.scalar_one()
        

        except Exception:
            await self.session.rollback()
            return None  # Сигнализируем сервису, что транзакция упала

    async def get_all_cars_with_owners(self) -> List[CarModel]:
        # 1. Загружаем CarModel
        # 2. Через selectinload подгружаем список CarModel.ownerships
        # 3. Через chained selectinload подгружаем UserCarOwnership.user для каждой записи
        query = (
            select(CarModel)
            .options(
                selectinload(CarModel.ownerships)
                .selectinload(UserCarOwnership.user)
        )
    )
        result = await self.session.execute(query)
        # scalars().all() вернет чистый список объектов CarModel с уже заполненными связями в памяти
        return list(result.scalars().all())

    async def get_car_by_vin(self, vin_number: str) -> Optional[CarModel]:
        result = await self.session.execute(
            select(CarModel).where(
                func.lower(CarModel.vin_number) == vin_number.lower()
            )
        )
        return result.scalar_one_or_none()

    async def get_car_by_reg_number(self, reg_number: str) -> Optional[CarModel]:
        result = await self.session.execute(
            select(CarModel).where(
                func.lower(CarModel.reg_number) == reg_number.lower()
            )
        )
        return result.scalar_one_or_none()

    async def get_car_by_id(self, car_id: str) -> Optional[CarModel]:
        stmt = (
            select(CarModel).where(CarModel.id == car_id)
            # Загружаем связи сразу в одном запросе
            .options(joinedload(CarModel.ownerships).joinedload(UserCarOwnership.user))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
