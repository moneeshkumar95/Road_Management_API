import os
from datetime import timedelta
from enum import Enum
from functools import lru_cache
from cryptography.fernet import Fernet

from passlib.context import CryptContext
from pydantic_settings import BaseSettings


class EnvironmentOption(Enum):
    """
    Enumeration for defining the different environments the application can run in.

    This enum class represents the possible environments for the application,
    allowing for clear and consistent management of environment-specific configurations.

    Attributes:
        Dev (str): The development environment.
        Stage (str): The staging environment.
        Prod (str): The production environment.
    """

    Dev = "Dev"
    Stage = "Stage"
    Prod = "Prod"


class Settings(BaseSettings):
    """
    Configuration settings for the API application.

    This class defines all the necessary settings for the application,
    including environment configurations, JWT settings, allowed origins,
    and password hashing context.

    Attributes:
        ENV (str): The environment in which the application is running (e.g., 'dev', 'prod').
        IS_DEV_ENV (bool): A flag indicating whether the environment is 'dev'.
        APP_TITLE (str): The title of the application, which includes the current environment.
        APP_VERSION (str): The version of the application.
        ALLOWED_ORIGINS (list): A list of allowed origins for Cross-Origin Resource Sharing (CORS).
        EXCLUDED_ROUTES_HEADER (list): A list of routes that are excluded from header checks.
        JWT_SECRET_KEY (str): The secret key used to sign JWT tokens.
        JWT_ALGORITHM (str): The algorithm used for encoding JWT tokens.
        JWT_ACCESS_TOKEN_EXPIRE (timedelta): The expiration time for access tokens.
        JWT_REFRESH_TOKEN_EXPIRE (timedelta): The expiration time for refresh tokens.
        PWD_CONTEXT (CryptContext): The password hashing context, set to use the bcrypt algorithm.
        CELERY_APP (Celery): The Celery App Instance.
    """

    # Current Environment
    ENV: str = EnvironmentOption[os.getenv("ENV", EnvironmentOption.Dev.value).capitalize()].value
    IS_DEV_ENV: bool = EnvironmentOption.Dev.value == ENV

    # App settings
    APP_TITLE: str = f"Road Management API {ENV}"
    APP_VERSION: str = "1.0"

    # Allowed origins for CORS
    ALLOWED_ORIGINS: list[str] = ["*"]

    # Allowed routes without checking in header
    EXCLUDED_ROUTES_HEADER: set[str] = {
        "/docs",
        "/openapi.json",
        "/api/v1/health_check",
        "/api/v1/auth/login"
    }

    # For JWT
    JWT_SECRET_KEY: str = os.environ.get("JWT_SECRET_KEY")
    JWT_ALGORITHM: str = os.environ.get("JWT_ALGORITHM")
    JWT_ACCESS_TOKEN_EXPIRE: timedelta = timedelta(days=30)
    JWT_REFRESH_TOKEN_EXPIRE: timedelta = timedelta(days=180)

    # Setup context with bcrypt algorithm
    PWD_CONTEXT: CryptContext = CryptContext(schemes=["bcrypt"], deprecated="auto")

    # For Cryptography
    CRYPTO_SECRET_KEY: bytes = b"bi-0p-AmtARr_aS1TnY2PPtdA65Kvu6G4ulF_2P1uUE="
    CRYPTO_CIPHER_SUITE: Fernet = Fernet(CRYPTO_SECRET_KEY)

    # For Database
    DATABASE_URL: str = os.environ.get("DATABASE_URL")


@lru_cache
def get_settings() -> Settings:
    """
    Retrieve the application settings.

    Returns:
        Settings: The application settings.
    """
    return Settings()


# Initialize settings
app_settings: Settings = get_settings()