import json

from fastapi import UploadFile, File, Depends, Form
from fastapi.responses import JSONResponse
from sqlmodel import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from geoalchemy2.shape import from_shape
from shapely.geometry import shape

from ..models import RoadNetworkModel, EdgeModel
from src.global_utils import success_response, error_response
from src.database import get_db
from src.apps.auth.utils import get_current_user
from src.apps.user.models import UserModel



async def update_road_network(
    name: str = Form(...),
    version: float = Form(...),
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_db),
    user: UserModel = Depends(get_current_user),
) -> JSONResponse:
    """
    Updates an existing road network by creating a new version from an uploaded .geojson file. Marks edges from the previous version as inactive.

    Args:
        name (str): Name of the road network to update.
        version (float): New version number, must be higher than the current latest version.
        file (UploadFile): A .geojson file containing updated road network geometry.
        
    Returns:
        JSONResponse: A success message upon successful update, or an error message with the appropriate status code.
    """
    try:
        if not file.filename.endswith(".geojson"):
            return error_response(
                status_code=400, 
                detail="Only .geojson files allowed"
            )
        
        # Fetch latest_network
        latest_network_query = (
            select(RoadNetworkModel)
            .where(RoadNetworkModel.name == name)
            .where(RoadNetworkModel.customer_id == user.customer_id)
            .order_by(RoadNetworkModel.version.desc())
            .limit(1)
        )
        latest_network_result = await session.execute(latest_network_query)
        latest_network = latest_network_result.scalar_one_or_none()

        if not latest_network:
            return error_response(
                status_code=404, 
                detail=f"Road network `{name}` not found"
        )

        if version <= latest_network.version:
            return error_response(
                status_code=400,
                detail=f"New version `({version})` must be higher than current latest `({latest_network.version})`"
            )
        
        # Parse GeoJSON
        content = await file.read()
        geojson_data = json.loads(content)

        # Mark all old edges as inactive
        await session.execute(
            update(EdgeModel)
            .where(EdgeModel.network_id == latest_network.id)
            .values(is_active=False)
        )

        # Create new RoadNetwork as updated version
        new_network = RoadNetworkModel(
            name=latest_network.name,
            version=version,
            customer_id=user.customer_id
        )
        session.add(new_network)
        await session.flush()

        edges = []
        # Add new edges
        for feature in geojson_data.get("features", []):
            geometry_obj = shape(feature["geometry"])
            geom = from_shape(geometry_obj, srid=4326)

            edge = EdgeModel(
                network_id=new_network.id,
                geometry=geom,
                properties=feature.get("properties", {}),
                is_active=True
            )
            edges.append(edge)

        session.add_all(edges)

        await session.commit()

        return success_response(
            detail="Road network updated successfully"
        )
    except SQLAlchemyError as e:
        await session.rollback()
        return error_response(
            status_code=500,
            detail=f"Error occured during updating roadnetwork"
        )
    except json.JSONDecodeError:
        return error_response(
            status_code=400, 
            detail="Only .geojson files allowed"
        )