from fastapi import FastAPI
from contextlib import asynccontextmanager

from src.database import engine
from src.database import Base


from src.api import main_router


# В FastAPI 0.93+ вместо on_event("startup") рекомендуется lifespan:
@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    # при остановке корректно закрывает пул соединений
    await engine.dispose()


app = FastAPI(lifespan=lifespan)

app.include_router(main_router)
