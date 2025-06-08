from datetime import datetime, timedelta

import jwt
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer

from src.apps.user.models import UserModel, UserType
from src.database import get_db
from src.settings import app_settings
from .schemas import UserLoginSchema


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


async def get_login_data(request: Request) -> UserLoginSchema:
    """
    Extracts login data from an incoming request, supporting both form-encoded and JSON payloads.

    Args:
        request (Request): The incoming HTTP request containing the login data.

    Returns:
        UserLoginSchema: An instance of UserLoginSchema containing the username and password.

    Raises:
        HTTPException: If the request data is invalid or cannot be processed, raises a 422 Unprocessable Entity error.
    """
    try:
        form = await request.form()
        return UserLoginSchema(username=form.get("username"), password=form.get("password"))
    except Exception:
        try:
            json_body = await request.json()
            return UserLoginSchema(**json_body)
        except (ValidationError, ValueError) as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid request"
            ) from e


def create_token(user: UserModel, expires_delta: timedelta) -> str:
    """
    Generates a JSON Web Token (JWT) for the specified user with an expiration time.

    Args:
        user (UserModel): The user object containing user details such as ID and role.
        expires_delta (timedelta): The duration for which the token remains valid.

    Returns:
        str: The encoded JWT as a string.
    """
    to_encode = {"user_id": user.id}

    expire = datetime.now() + expires_delta
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, app_settings.JWT_SECRET_KEY, algorithm=app_settings.JWT_ALGORITHM)

    return encoded_jwt


def create_access_token(user: UserModel) -> str:
    """
    Generates an access token for the specified user with a predefined expiration time.

    Args:
        user (UserModel): The user object for whom the access token is generated.

    Returns:
        str: The encoded access token as a string.
    """
    return create_token(user, expires_delta=app_settings.JWT_ACCESS_TOKEN_EXPIRE)


def create_refresh_token(user: UserModel) -> str:
    """
    Generates a refresh token for the specified user with a predefined expiration time.

    Args:
        user (UserModel): The user object for whom the refresh token is generated.

    Returns:
        str: The encoded refresh token as a string.
    """
    return create_token(user, expires_delta=app_settings.JWT_REFRESH_TOKEN_EXPIRE)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    sesssion: AsyncSession = Depends(get_db),  # noqa: B008
) -> UserModel:
    """
    Retrieves the current authenticated user based on the provided JWT token.

    Args:
        token (str): The JWT token provided by the OAuth2 scheme for authentication.
        sesssion (AsyncSession): The database session for executing queries.

    Returns:
        UserModel: The authenticated user object.

    Raises:
        HTTPException: If the token is invalid, expired, or the user cannot be found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid Token"
    )

    try:
        payload = jwt.decode(token, app_settings.JWT_SECRET_KEY, algorithms=[app_settings.JWT_ALGORITHM])

        user_id: int = payload.get("user_id")

        if not user_id:
            raise credentials_exception

    except jwt.ExpiredSignatureError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired") from e
    except jwt.PyJWTError as e:
        raise credentials_exception from e

    query = (
        select(UserModel)
        .where(UserModel.id == user_id)
        )
    result = await sesssion.execute(query)
    user = result.unique().scalar_one_or_none()

    if not user:
        raise credentials_exception

    return user


async def get_current_admin_user(
    user: UserModel = Depends(get_current_user),
) -> UserModel:
    """
    Dependency that returns the current user only if they are an admin.

    Args:
        user (UserModel): The current authenticated user.

    Returns:
        UserModel: The authenticated admin user.

    Raises:
        HTTPException: If the user is not an admin.
    """
    if user.type != UserType.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action"
        )
    return user


def is_json_check(request: Request) -> bool:
    """
    Checks if the request has a content type of 'application/json'.

    Args:
        request (Request): The HTTP request to check.

    Returns:
        bool: True if the content type is 'application/json', False otherwise.
    """
    return request.headers.get("content-type") == "application/json"
