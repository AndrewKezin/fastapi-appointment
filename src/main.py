from fastapi import FastAPI
from contextlib import asynccontextmanager

from src.database import engine
from src.database import Base 


from src.api import main_router

# В FastAPI 0.93+ вместо on_event("startup") рекомендуется lifespan:
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all) # conn.run_sync(...) нужен потому, что create_all — синхронная функция, а соединение асинхронное: run_sync выполняет её в отдельном потоке
    print("Database created")
    yield
    # при остановке корректно закрывает пул соединений
    await engine.dispose()
    print("Database closed")

app = FastAPI(lifespan=lifespan)

app.include_router(main_router)