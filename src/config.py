from pydantic import BaseModel
from pydantic_settings import BaseSettings
from pathlib import Path  # работа с путями в ОС

BASE_DIR = Path(
    __file__
).parent.parent  # родительская директория от текущего раположения файла


class AuthJWT(BaseModel):
    private_key_path: Path = BASE_DIR / "certs" / "jwt-private.pem"
    public_key_path: Path = BASE_DIR / "certs" / "jwt-public.pem"
    algorithm: str = "RS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30


class Settings(BaseSettings):
    app_name: str = "FastApi learn Appointments API"
    debug: bool = True  # режим разработки
    database_url: str = f"sqlite+aiosqlite:///./service.db"
    cors_origins: list = ["http://localhost:3000", "http://localhost:8000"]

    static_dir: str = "static"
    images_dir: str = "static/images"

    auth_jwt: AuthJWT = AuthJWT()

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()  # инициализация настроек
