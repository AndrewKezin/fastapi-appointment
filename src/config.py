from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "FastApi learn Appointments API"
    debug: bool = True # режим разработки
    database_url: str = "sqlite+aiosqlite:///service.db"
    cors_origins: list = [
        "http://localhost:3000", 
        "http://localhost:8000"
    ]

    static_dir: str = "static"
    images_dir: str = "static/images"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings() # инициализация настроек