from fastapi import Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ..schemas import CreateCustomerSchema
from ..models import CustomerModel
from src.global_utils import success_response, error_response
from src.apps.user.models import UserModel
from src.database import get_db
from src.apps.auth.utils import get_current_admin_user


async def create_customer(
    payload: CreateCustomerSchema,
    current_user: UserModel = Depends(get_current_admin_user),
    session: AsyncSession = Depends(get_db)
) -> JSONResponse:
    """
    Creates a new customer with the given details. Requires an admin user to perform the operation.

    Args:
        payload (CreateCustomerSchema): Customer data including the name.
        current_user (UserModel): Currently authenticated admin user dependency.
        session (AsyncSession): Database session dependency.

    Returns:
        JSONResponse: A success message upon successful customer creation, or an error message with the appropriate status code.
    """
    try:
        customer = CustomerModel(
            name=payload.name,
        )
        session.add(customer)
        await session.commit()

        return success_response(
            detail="Customer created successfully"
        )
    
    except IntegrityError as e:
        await session.rollback()
        return error_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Customer with this name already exists"
        )
    
    except Exception as e:
        await session.rollback()
        return error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error while creating customer"
        )
