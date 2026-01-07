# app/adapters/database.py

from typing import AsyncGenerator
import logging

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings


logger = logging.getLogger(__name__)


# Declarative Base (shared by all ORM models)
class Base(DeclarativeBase):

    """
    Base class for all SQLAlchemy ORM models.

    All models across the application MUST inherit from this Base.
    Alembic will also reference this Base for migrations.
    """

    pass

try:
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,      # SQL echo only in development
        pool_pre_ping=True,       # Detect dropped connections
        pool_size=10,             # Sensible default
        max_overflow=20,          # Burst handling
        future=True,
    )

except Exception as exc:
    logger.critical("Failed to create database engine")
    raise RuntimeError("Database engine initialization failed") from exc


# Session Generator
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


# Session Dependency / Provider
async def get_db() -> AsyncGenerator[AsyncSession, None]:

    """
    Provides a scoped async database session.

    This function is intended to be used as:
    - FastAPI dependency
    - Service-level session provider
    - Background task session provider

    It guarantees:
    - One session per request/task
    - Proper cleanup
    - No connection leaks
    """

    session: AsyncSession = AsyncSessionLocal()

    try:
        yield session
        await session.commit()

    except SQLAlchemyError as exc:
        await session.rollback()
        logger.exception("Database transaction failed")
        raise

    finally:
        await session.close()



async def close_engine() -> None:
    """
    Gracefully dispose the database engine.

    Call this during application shutdown if needed.
    """
    try:
        await engine.dispose()
        logger.info("Database engine disposed successfully")
    except Exception as exc:
        logger.exception("Error while disposing database engine")
