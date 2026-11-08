# import sys
# from pathlib import Path

# Добавляем корень проекта в sys.path, чтобы импорты из src/ работали из консоли. Это не нужно, если запускать через "python -m src.seed.run"
# sys.path.append(str(Path(__file__).parent.parent.parent))

import asyncio

from sqlalchemy import delete

from src.database import new_session
from src.models import UserModel, CarModel, UserCarOwnership
from src.seed.data_generators import create_test_user, create_test_car


async def seed_database():
    print("🚀 Старт посева данных...")

    # Открываем сессию вручную через фабрику сессий, так как Depends вне эндпоинтов FastAPI не работает
    async with new_session() as session:
        async with session.begin():  # Автоматически сделает commit() в конце, если не будет ошибок
            # ОЧИСТКА: Удаляем старые связи, чтобы избежать UNIQUE constraint failed
            await session.execute(delete(UserCarOwnership))
            await session.execute(delete(UserModel))
            await session.execute(delete(CarModel))

            # генерация пользователей
            users = []
            for _ in range(10):
                user_data = create_test_user()

                # Создаем экземпляр модели, распаковывая словарь через **. После распаковки user = UserModel(**user) переменная user станет полноценным SQLAlchemy-объектом, у которого после await session.flush() автоматически появится user.id, что решит проблему для создания связей ниже.
                user = UserModel(**user_data)
                session.add(user)

                # Сохраняем именно ORM-объект, чтобы потом у него забрать id
                users.append(user)

            # генерация автомобилей
            cars = []
            for _ in range(10):
                car_data = create_test_car()
                car = CarModel(**car_data)
                session.add(car)
                cars.append(car)

            # генерация id для юзеров и машин
            await session.flush()

            # генерация связей
            for user in users:
                random_car = cars.pop()

                ownership = UserCarOwnership(
                    user_id=user.id, car_id=random_car.id, is_primary=True
                )

                session.add(ownership)

        print("✅ Посев успешно завершен! База данных заполнена фейковыми данными.")


if __name__ == "__main__":
    # Запускаем асинхронную функцию
    asyncio.run(seed_database())
