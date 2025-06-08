from fastapi import Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import select

from ..models import RoadNetworkModel
from src.database import get_db
from src.global_utils import success_response, error_response
from src.apps.user.models import UserModel
from src.apps.auth.utils import get_current_user


async def list_road_networks(
    session: AsyncSession = Depends(get_db),
    user: UserModel = Depends(get_current_user)
) -> JSONResponse:
    """
    Retrieves a list of road networks belonging to the authenticated user's customer.

    Returns:
        JSONResponse: A success response containing the list of road networks, or an error message with the appropriate status code.
    """
    try:
        filters = [RoadNetworkModel.customer_id == user.customer_id]

        road_networks_query = (
            select(RoadNetworkModel)
            .where(*filters)
            .order_by(
                RoadNetworkModel.name.asc(), 
                RoadNetworkModel.version.desc()
            )
        )
        road_networks_result = await session.execute(road_networks_query)
        road_networks = road_networks_result.scalars().all()

        return success_response(
            detail="Road Network List retrieved successfully",
            data=road_networks
        )
    except SQLAlchemyError as e:
        await session.rollback()
        return error_response(
            status_code=500,
            detail=f"Error occured while fetching road networks"
        )