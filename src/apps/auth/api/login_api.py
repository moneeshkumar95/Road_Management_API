from typing import Annotated

from fastapi import Depends, status
from fastapi.responses import JSONResponse
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.sql import select

from src.apps.user.models import UserModel
from src.database import get_db
from src.global_utils import success_response, error_response
from src.settings import app_settings
from ..schemas import UserLoginSchema
from ..utils import (
    create_access_token,
    create_refresh_token,
    get_login_data,
    is_json_check,
)


async def login(
    is_json: Annotated[bool, Depends(is_json_check)],
    payload: Annotated[UserLoginSchema, Depends(get_login_data)],
    session: Annotated[AsyncSession, Depends(get_db)]
    ) -> JSONResponse:
    """
    Authenticates the user based on the provided credentials (username and password), generates access & refresh tokens & returns the user details.

    Args:
        is_json (bool): A flag indicating whether the response should be in JSON format.
        payload (UserLoginSchema): The schema containing the username and password provided by the user for login.

    Returns:
        success_response: If the credentials are valid & the user is active, returns the access token, refresh token,
                          user ID & user type in the response.
        error_response:
            - If the user credentials are invalid, returns HTTP 401 UNAUTHORIZED with an "Invalid credentials" error message.
            - If the user account is inactive, returns HTTP 403 FORBIDDEN with an "Account is inactive" error message.
    """
    # Check if the user exists
    query = (
        select(UserModel)
        .where(UserModel.username == payload.username)
    )
    result = await session.execute(query)
    user = result.unique().scalar_one_or_none()

    # Check password is correct
    if not user or not await run_in_threadpool(app_settings.PWD_CONTEXT.verify, payload.password, user.hashed_password):
        return error_response(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    # Check if the user is active
    if not user.is_active:
        return error_response(status_code=status.HTTP_403_FORBIDDEN, detail="Account is inactive")

    response_data = {
        "access_token": create_access_token(user),
        "refresh_token": create_refresh_token(user),
        "user_id": user.id
    }

    # Return the response data if the request is not JSON (For swagger UI)
    if not is_json:
        return response_data

    return success_response(
        detail="Login successfully", 
        data=response_data
    )
