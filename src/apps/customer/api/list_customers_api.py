from fastapi import Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import select

from ..models import CustomerModel
from src.database import get_db
from src.global_utils import success_response, error_response
from src.apps.user.models import UserModel
from src.apps.auth.utils import get_current_admin_user


async def list_customers(
    session: AsyncSession = Depends(get_db),
    user: UserModel = Depends(get_current_admin_user)
) -> JSONResponse:
    """
    Retrieves a list of all customers in the system.

    Returns:
        JSONResponse: A success response with a list of customers, or an error response with status code 500
        if a database error occurs.
    """
    try:
        customers_query = (
            select(CustomerModel)
            .order_by(
                CustomerModel.name.asc()
            )
        )
        customers_result = await session.execute(customers_query)
        customers = customers_result.scalars().all()

        return success_response(
            detail="Customers List retrieved successfully",
            data=customers
        )
    except SQLAlchemyError as e:
        await session.rollback()
        return error_response(
            status_code=500,
            detail=f"Error occured while fetching customers"
        )