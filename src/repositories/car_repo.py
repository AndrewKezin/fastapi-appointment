from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import desc, select, update
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
            .outerjoin(CarModel.ownerships)  # лучше outerjoin, чтобы машина нашлась, даже если владельцев пока 0
            .where(CarModel.id == car_id)
            .order_by(desc(UserCarOwnership.ownership_start))
            .options(
                contains_eager(CarModel.ownerships).selectinload(UserCarOwnership.user)
            )
            .execution_options(populate_existing=True)  # гарантирует обновление связей после update/commit
        )
        result = await self.session.execute(stmt)

        return result.unique().scalar_one_or_none()

    # для проверки vin перед добавлением или изменением данных авто
    async def get_car_by_vin(self, vin_number: str) -> Optional[CarModel]:
        stmt = select(CarModel).where(CarModel.vin_number == vin_number.upper())
        result = await self.session.execute(stmt)

        return result.scalar_one_or_none()

    # для проверки рег.номера перед изменением данных авто
    async def get_car_by_reg_number(self, reg_number: str) -> Optional[CarModel]:
        stmt = select(CarModel).where(CarModel.reg_number == reg_number.upper())
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

    async def update_car(
        self,
        car: CarModel,
        update_data: dict[str, str | int | float],
        owner_id: Optional[str] = None,
        is_primary_owner: bool = True,
    ) -> CarModel:
        try:
            # Обновляем поля самой таблицы cars, если они переданы
            for key, value in update_data.items():
                setattr(car, key, value)

            # Обрабатываем логику владельца, если передан owner_id
            if owner_id is not None:
                now = datetime.now(timezone.utc)

                # Ищем активную запись владения для переданного пользователя
                active_user_stmt = select(UserCarOwnership).where(
                    UserCarOwnership.car_id == car.id,
                    UserCarOwnership.user_id == owner_id,
                    UserCarOwnership.ownership_end.is_(None),
                )
                active_user_res = await self.session.execute(active_user_stmt)
                active_user_ownership = active_user_res.scalar_one_or_none()

                # Если назначаем нового основного владельца, сбрасываем флаг у предыдущих
                if is_primary_owner:
                    # Если пользователь УЖЕ является текущим основным владельцем — ничего не меняем
                    if active_user_ownership and active_user_ownership.is_primary:
                        pass
                    else:
                        # Закрываем период владения у текущего основного владельца (если он есть)
                        close_prev_primary_stmt = (
                            update(UserCarOwnership)
                            .where(
                                UserCarOwnership.car_id == car.id,
                                UserCarOwnership.is_primary.is_(True),
                                UserCarOwnership.ownership_end.is_(None),
                            )
                            .values(is_primary=False, ownership_end=now)
                        )
                        await self.session.execute(close_prev_primary_stmt)

                        # Если новый основной владелец до этого был активным дополнительным,
                        # закрываем его старый период и открываем новый в статусе основного
                        if active_user_ownership:
                            active_user_ownership.ownership_end = now

                        new_primary_ownership = UserCarOwnership(
                            user_id=owner_id,
                            car_id=car.id,
                            is_primary=True,
                            ownership_start=now,
                        )
                        self.session.add(new_primary_ownership)

                else:
                    # Добавление дополнительного владельца (is_primary=False)
                    # Создаем запись только если у пользователя еще нет активного владения этим авто
                    if not active_user_ownership:
                        new_secondary_ownership = UserCarOwnership(
                            user_id=owner_id,
                            car_id=car.id,
                            is_primary=False,
                            ownership_start=now,
                        )
                        self.session.add(new_secondary_ownership)

            # Фиксируем все изменения одной транзакцией
            await self.session.commit()

            # Перечитываем актуальный объект со связями (как в create_car)
            return await self.get_car_by_id_with_owners(car.id)

        except Exception as e:
            await self.session.rollback()
            print("Error updating car: ", e)
            return None  # сигнализируем сервису, что транзакция упала
