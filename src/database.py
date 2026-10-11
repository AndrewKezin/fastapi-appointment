from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from .config import settings


engine = create_async_engine(settings.database_url, echo=True) # echo=True покажет SQL-запросы в консоль — удобно на этапе разработки

new_session = async_sessionmaker(engine, expire_on_commit=False)

# Ключевой момент — yield. Благодаря ему FastAPI может выполнить код после запроса (закрытие сессии, commit/rollback). Если просто return session, сессия не закроется и будут утечки соединений.
async def get_session():
    async with new_session() as session:
        yield session

class Base(DeclarativeBase):
    pass
