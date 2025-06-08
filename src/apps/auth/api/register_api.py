from fastapi import Depends, status
from fastapi.responses import JSONResponse
from fastapi.concurrency import run_in_threadpool
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.exc import IntegrityError

from ..utils import get_current_admin_user
from ..schemas import UserRegisterSchema
from src.global_utils import success_response, error_response
from src.settings import app_settings
from src.apps.user.models import UserModel
from src.database import get_db


async def register(
    payload: UserRegisterSchema,
    current_user: UserModel = Depends(get_current_admin_user),
    session: AsyncSession = Depends(get_db)
) -> JSONResponse:
    """
    Registers a new user with the provided registration data. Requires an admin user to perform the operation.

    Args:
        payload (UserRegisterSchema): User registration data including username, email, password, and other details.

    Returns:
        JSONResponse: A success message upon successful user creation, or an error message with the appropriate status code.
    """
    try:
        if payload.password != payload.conform_password:
            return error_response(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Passwords do not match"
            )
        
        payload.password = await run_in_threadpool(app_settings.PWD_CONTEXT.hash, payload.password)

        user_data = payload.model_dump(exclude={"conform_password", "password"})
        user_data["hashed_password"] = payload.password

        # Create a new user
        new_user = UserModel(
            **user_data, 
            created_by=current_user.id, 
            updated_by=current_user.id
        )
        session.add(new_user)

        await session.commit()

        return success_response(
            detail="User created successfully"
        )
    except IntegrityError as e:
        await session.rollback()

        error_msg = str(e.orig)

        status_code = status.HTTP_400_BAD_REQUEST
        detail = "Username or Email already exists"

        if "foreign key constraint" in error_msg.lower() or "violates foreign key" in error_msg.lower():
            detail="Invalid customer_id"

        return error_response(
            status_code=status_code,
            detail=detail
        )