from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic_settings import BaseSettings
from sqlalchemy import text, select
from sqlmodel import SQLModel
from asyncpg.exceptions import (
    InvalidAuthorizationSpecificationError, InvalidCatalogNameError, InvalidPasswordError
)

from .custom_middleware import LoggingMiddleware
from .database import async_session, engine
from .apps.customer.models import CustomerModel
from .apps.user.models import UserModel, UserType
from .apps.road_network.models import RoadNetworkModel, EdgeModel
from .settings import app_settings

async def init_db():
    async with engine.begin() as conn:
        # Enable PostGIS extension first
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))

        # Create all tables
        await conn.run_sync(SQLModel.metadata.create_all)

    # Insert initial data for Customer & User
    async with async_session() as session:
        result = await session.execute(select(CustomerModel.id).limit(1))
        existing_customer = result.scalars().first()

        if existing_customer:
            return None

        hashed_password = app_settings.PWD_CONTEXT.hash("RoadNetwork@123")

        # For 1st customer & user
        munich = CustomerModel(name="Munich City Roads Department".lower())
        session.add(munich)
        await session.flush()

        munich_user = UserModel(
            username="munich_admin",
            email="admin@munich.gov",
            hashed_password=hashed_password,
            full_name="Munich Admin",
            customer_id=munich.id,
            type=UserType.ADMIN
        )
        session.add(munich_user)
        await session.flush()

        # For 2nd customer & user
        berlin = CustomerModel(name="Berlin Transport Authority".lower())
        session.add(berlin)
        await session.flush()

        berlin_user = UserModel(
            username="berlin_admin",
            email="admin@berlin.gov",
            hashed_password=hashed_password,
            full_name="Berlin Admin",
            customer_id=berlin.id,
            type=UserType.USER
        )
        session.add(berlin_user)

        await session.flush()

        await session.commit()


def lifespan_factory() -> callable:
    """
    Factory function that creates a lifespan async context manager for a FastAPI app.

    Returns:
        callable: The lifespan async context manager.
    """

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator:
        """
        Async context manager that handles the lifespan of a FastAPI app.

        Args:
            app (FastAPI): The FastAPI app instance.

        """
        await init_db()
        # try:
        #     # Postgres Ping
        #     async with async_session() as session:
        #         await session.execute(select(1))
        # except (
        #     ConnectionRefusedError, InvalidAuthorizationSpecificationError, InvalidCatalogNameError, InvalidPasswordError
        # ) as e:
        #     raise Exception(f"Failed to connect to Postgres DB: {e}")

        print("Worker started successfully")

        yield

        # await engine.dispose()

        print("Worker stopped successfully")

    return lifespan


def create_application(app_settings: BaseSettings, router: APIRouter) -> FastAPI:
    """
    Creates and configures a FastAPI application based on the provided settings.

    Args:
        app_settings (BaseSettings): The BaseSettings object containing the application settings.
        router (APIRouter): The APIRouter object containing the routes to be included in the FastAPI application.

    Returns:
        FastAPI: A fully configured FastAPI application instance.
    """
    # setup_logging()

    # Before creating the FastAPI application
    lifespan = lifespan_factory()

    application = FastAPI(
        title=app_settings.APP_TITLE,
        version=app_settings.APP_VERSION,
        lifespan=lifespan,
    )

    # Adding middleware
    application.add_middleware(
        CORSMiddleware,
        allow_origins=app_settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add the ASGI middleware
    application.add_middleware(LoggingMiddleware)

    # Including main router
    application.include_router(router)

    # App Health Check
    @application.get("/api/v1/health_check", tags=["Health Check"])
    async def health_status() -> dict:
        """
        Endpoint for Health Check

        Returns:
            dict: The response for the health check.
        """
        return {"status": status.HTTP_200_OK, "detail": "OK"}

    return application
