import os
from typing import AsyncGenerator

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from asyncpg.exceptions import (
    InvalidAuthorizationSpecificationError, InvalidCatalogNameError, InvalidPasswordError
)

from .settings import app_settings


# Define the metadata
meta_data = MetaData()

# Define the base class for declarative models
Base = SQLModel.metadata

# Create the engine with connection pooling
engine = create_async_engine(
    app_settings.DATABASE_URL,
    future=True,
    pool_size=10,
    max_overflow=5,
    pool_recycle=1800,
    pool_timeout=60,
    pool_pre_ping=True
)

# Session
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Returns an asynchronous generator that yields a database session.

    Yields:
        AsyncSession: An asynchronous database session.

    Raises:
        OperationalError: If there is a failure to connect to the database.
    """
    session = async_session()

    try:
        yield session
    except (
        ConnectionRefusedError, InvalidAuthorizationSpecificationError, InvalidCatalogNameError,
        InvalidPasswordError
    ) as e:
        raise Exception(f"Failed to connect to Postgres DB: {e}")
    finally:
        await session.close()
