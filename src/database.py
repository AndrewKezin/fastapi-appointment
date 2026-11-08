from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import event

from .config import settings

engine = create_async_engine(
    url=settings.database_url,
    echo=settings.debug,  # echo=True покажет SQL-запросы в консоль — удобно на этапе разработки, но в продакшене нужно обязательно отключить
)


# Важнейший хук для SQLite
# Настройка события для асинхронного соединения
@event.listens_for(engine.sync_engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


new_session = async_sessionmaker(engine, expire_on_commit=False)


# Ключевой момент — yield. Благодаря ему FastAPI может выполнить код после запроса (закрытие сессии, commit/rollback). Если просто return session, сессия не закроется и будут утечки соединений.
async def get_session():
    async with new_session() as session:
        yield session


class Base(DeclarativeBase):
    # __abstract__ = True  # Указывает, что таблицу создавать не нужно

    # id: Mapped[int] = mapped_column(primary_key=True)  # Указывает, что поле id будет одинаковым и будет у всех таблиц
    pass
