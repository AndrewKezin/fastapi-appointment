import random
import string


# car generators
def generate_vin() -> str:
    vin_alphabet = "0123456789ABCDEFGHJKLMNPRSTUVWXYZ"
    return "".join([random.choice(vin_alphabet) for _ in range(17)])

def generate_reg_number() -> str:
    reg_number_alphabet = "АВКМНОРСТУХ"
    return f"{random.choice(reg_number_alphabet)}{random.randint(100, 999)}{"".join(random.choices(reg_number_alphabet, k=2))}{random.randint(10, 999)}"

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

def generate_year() -> int:
    return random.randint(2000, 2025)

def generate_engine_volume() -> float | None:
    return round(random.uniform(1.0, 3.0), 1)

def generate_color() -> str | None:
    colors = ["Белый", "Черный", "Серый", "Красный", "Синий", "Зеленый", "Желтый", None]
    return random.choice(colors)


# user generators
alphabet = string.ascii_letters + string.digits

def generate_email():
    return f"{"".join(random.choices(alphabet, k=(random.randint(5, 10))))}@{random.choice(["mail.ru", "gmail.com", "yandex.ru"])}"

# def generate_password():
#     return "".join(random.choices(alphabet, k=(random.randint(5, 10))))

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


def create_test_user() -> dict:
    user_fio = generate_name()

    return {
        "email": generate_email(),
        "hashed_password": "11111",
        "first_name": user_fio["name"],
        "middle_name": user_fio["patronymic"],
        "last_name": user_fio["last_name"],
        "phone": generate_phone(),
        "address": generate_address()
    }


def create_test_car() -> dict:
    return {
        "vin_number": generate_vin(),
        "reg_number": generate_reg_number(),
        "brand": generate_brand_model()["brand"],
        "model": generate_brand_model()["model"],
        "year": generate_year(),
        "engine_volume": generate_engine_volume(),
        "color": generate_color(),
    }



# if __name__ == "__main__":
#     print(create_test_car())