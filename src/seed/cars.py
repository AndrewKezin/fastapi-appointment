import random

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.services.car_service import CarService

def generate_vin() -> str:
    vin_alphabet = "0123456789ABCDEFGHJKLMNPRSTUVWXYZ"
    return "".join([random.choice(vin_alphabet) for _ in range(17)])

def generate_reg_number() -> str:
    reg_number_alphabet = "АВКМНОРСТУХ"
    return f"{random.choice(reg_number_alphabet)}{random.randint(100, 999)}{(random.choice(reg_number_alphabet))*2}{random.randint(10, 999)}"

def generate_brand_model() -> dict:
    brands = ["Audi", "VW", "Skoda", "Seat"]

    au = ["A1", "A3", "A4", "A5", "A6", "A7", "A8", "Q7", "Q8"]
    vw = ["Golf", "Passat", "Tiguan", "Touareg", "Transporter", "Talagon"]
    sk = ["Octavia", "Rapid", "Superb", "Yeti", "Kodiaq", "Karoq"]
    seat = ["Altea", "Ibiza", "Leon"]

    brand = random.choice(brands)
    model = None

    if brand == "Audi":
        model = random.choice(au)
    elif brand == "VW":
        model = random.choice(vw)
    elif brand == "Skoda":
        model = random.choice(sk)
    elif brand == "Seat":
        model = random.choice(seat)

    return {"brand": brand, "model": model}

def generate_engine_volume() -> float | None:
    return round(random.uniform(1.0, 3.0), 1)

def generate_color() -> str | None:
    colors = ["Белый", "Черный", "Серый", "Красный", "Синий", "Зеленый", "Желтый", None]
    return random.choice(colors)

def generate_car() -> dict:
    return {
        "vin": generate_vin(),
        "reg_number": generate_reg_number(),
        "brand": generate_brand_model()["brand"],
        "model": generate_brand_model()["model"],
        "engine_volume": generate_engine_volume(),
        "color": generate_color(),
    }

async def create_test_cars(session: AsyncSession = Depends(get_session)):
    service = CarService(session)

    for _ in range(50):
        await service.add_car(generate_car())


# if __name__ == "__main__":
#     print("Example car:",generate_car())

