import random
import string

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.schemas.users import UserCreateSchema
from src.services.user_service import UserService

alphabet = string.ascii_letters + string.digits

def generate_email():
    return f"{"".join(random.choices(alphabet, k=(random.randint(5, 10))))}@{random.choice(["mail.ru", "gmail.com", "yandex.ru"])}"

def generate_password():
    return "".join(random.choices(alphabet, k=(random.randint(5, 10))))

def generate_name():
    male_names = ["Александр", "Алексей", "Иван", "Михаил", "Максим", "Никита", "Николай", "Павел", "Сергей", "Степан", "Федор", "Юрий"]
    femail_names = ["Анна", "Екатерина", "Елена", "Ирина", "Кристина", "Мария", "Наталья", "Ольга", "Светлана", "Татьяна", "Юлия"]

    male_patronymics = ["Иванович", "Сергеевич", "Александрович", "Михайлович", "Никитич", "Павлович", "Сергеевич", "Федорович", "Юрьевич","Владимирович", "Степанович"] 
    femail_patronymics = ["Ивановна", "Сергеевна", "Александровна", "Михайловна", "Никитична", "Павловна", "Сергеевна", "Федоровна", "Юрьевна","Владимировна", "Степановна"]

    male_last_names = ["Иванов", "Петров", "Смирнов", "Кузнецов", "Васильев", "Николаев", "Соколов", "Лебедев", "Козлов", "Павлов", "Морозов"]
    female_last_names = ["Иванова", "Петрова", "Смирнова", "Кузнецова", "Васильева", "Николаева", "Соколова", "Лебедева", "Козлова", "Павлова", "Морозова"]

    if random.randint(0, 1) == 0:
        return {
            "name": random.choice(male_names),
            "patronymic": random.choice(male_patronymics),
            "last_name": random.choice(male_last_names)
        }
    else:
        return {
            "name": random.choice(femail_names),
            "patronymic": random.choice(femail_patronymics),
            "last_name": random.choice(female_last_names)
        }

def generate_phone():
    return f"+7{''.join(random.choices('0123456789', k=10))}"

def generate_address():
    cities = ["Москва", "Мытищи", "Зеленоград", "Подольск", "Серпухов", "Красногорск", "Одинцово", "Клин", "Сергиев Посад", "Домодедово", "Троицк", "Солнечногорск", "Балашиха", "Егорьевск", "Видное", "Кашира", "Дмитров", "Электросталь", "Кашира", "Талдом"]
    streets = ["ул. Мира", "ул. Ленина", "ул. Красная", "ул. Космонавтов", "пр-т 40-летия Октября", "ул. Инженерная", "ул. Пушкина", "Лермонтовский б-р", "Солнечный пр-д"]

    return f"{random.choice(cities)}, {random.choice(streets)}, д.{random.randint(1, 100)}, кв.{random.randint(1, 300)}"

async def create_test_users(session: AsyncSession = Depends(get_session)):
    service = UserService(session)

    for _ in range(35):
        await service.create_user(UserCreateSchema(
            email=generate_email(),
            password=generate_password(),
            name=generate_name()["name"],
            patronymic=generate_name()["patronymic"],
            last_name=generate_name()["last_name"],
            phone=generate_phone(),
            address=generate_address()
        ))
