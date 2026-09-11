from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

# Engine asíncrono para PostgreSQL
engine = create_async_engine(
    settings.async_database_url,
    echo=(settings.LOG_LEVEL.upper() == "DEBUG"),
    future=True,
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600,
    pool_pre_ping=True
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)


class Base(DeclarativeBase):
    """Clase base declarativa para modelos SQLAlchemy"""
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency injection para sesiones de base de datos en endpoints FastAPI"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
