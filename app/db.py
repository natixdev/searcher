from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.settings import get_db_url


DATABASE_URL = get_db_url()

engine = create_async_engine(DATABASE_URL, pool_pre_ping=True)
async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


class Base(DeclarativeBase):
    """Базовый класс для моделей БД."""


async def get_db_session() -> AsyncGenerator[AsyncSession]:
    """Отдаёт асинхронную сессию БД."""

    async with async_session() as session:
        yield session
