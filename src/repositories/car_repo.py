from typing import List, Optional

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, contains_eager

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

            generated_car_id = car.id

            # Фиксируем обе записи одной транзакцией
            await self.session.commit()

            query = (
                select(CarModel)
                .where(CarModel.id == generated_car_id)
                .options(
                    selectinload(CarModel.ownerships).selectinload(
                        UserCarOwnership.user
                    )
                )
            )
            result = await self.session.execute(query)

            return result.scalar_one_or_none()

        except Exception as e:
            await self.session.rollback()
            print("Error:", e)
            return None  # Сигнализируем сервису, что транзакция упала

    async def get_all_cars_with_owners(self) -> List[CarModel]:
        query = (
            select(CarModel)
            .options(
                selectinload(CarModel.ownerships).selectinload(UserCarOwnership.user)
            )
            .order_by(desc(CarModel.created_at))
        )

        result = await self.session.execute(query)
        # scalars().all() вернет чистый список объектов CarModel с уже заполненными связями в памяти
        return list(result.scalars().all())

    async def get_car_by_id_with_owners(self, car_id: str) -> Optional[CarModel]:
        stmt = (
            select(CarModel)
            .join(CarModel.ownerships)
            .where(CarModel.id == car_id)
            .order_by(desc(UserCarOwnership.ownership_start))
            .options(
                contains_eager(CarModel.ownerships).selectinload(UserCarOwnership.user)
            )
        )
        result = await self.session.execute(stmt)

        return result.unique().scalar_one_or_none()

    # для проверки vin перед добавлением авто
    async def get_car_by_vin(self, vin_number: str) -> Optional[CarModel]:
        stmt = select(CarModel).where(CarModel.vin_number == vin_number.upper())
        result = await self.session.execute(stmt)

        return result.scalar_one_or_none()

    async def get_car_by_query_params(
        self,
        vin_number: str | None,
        reg_number: str | None,
        brand: str | None,
        model: str | None,
        limit: int,
        offset: int,
    ) -> List[CarModel]:
        stmt = (
            select(CarModel)
            .options(
                selectinload(CarModel.ownerships).selectinload(UserCarOwnership.user)
            )
            .order_by(desc(CarModel.updated_at))
        )

        if vin_number:
            stmt = stmt.where(CarModel.vin_number.ilike(f"%{vin_number}%"))

        if reg_number:
            stmt = stmt.where(CarModel.reg_number.ilike(f"%{reg_number}%"))

        if brand:
            stmt = stmt.where(CarModel.brand.ilike(f"%{brand}%"))

        if model:
            stmt = stmt.where(CarModel.model.ilike(f"%{model}%"))

        # пагинация
        stmt = stmt.limit(limit).offset(offset)

        result = await self.session.execute(stmt)

        return list(result.unique().scalars().all())
