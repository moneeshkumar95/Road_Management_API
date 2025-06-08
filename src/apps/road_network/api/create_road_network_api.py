import json

from fastapi import UploadFile, File, Depends, Form
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from geoalchemy2.shape import from_shape
from shapely.geometry import shape

from ..models import RoadNetworkModel, EdgeModel
from src.database import get_db
from src.global_utils import success_response, error_response
from src.apps.user.models import UserModel
from src.apps.auth.utils import get_current_user


async def create_road_network(
    name: str = Form(...),
    version: float = Form(...),
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_db),
    user: UserModel = Depends(get_current_user),
) -> JSONResponse:
    """
    Creates a new road network from an uploaded .geojson file.

    Args:
        name (str): Name of the road network.
        version (float): Version number of the road network.
        file (UploadFile): A .geojson file containing the road network geometry.

    Returns:
        JSONResponse: A success message upon successful upload, or an error message with the appropriate status code.
    """
    try:
        if not file.filename.endswith(".geojson"):
            return error_response(
                status_code=400, 
                detail="Only .geojson files allowed"
            )
        
        # Create RoadNetwork
        road_network = RoadNetworkModel(
            name=name,
            version=version,
            customer_id=user.customer_id
        )
        session.add(road_network)
        await session.flush()

        content = await file.read()
        geojson_data = json.loads(content)

        edges = []
        # Extract Features & Save as Edges
        for feature in geojson_data.get("features", []):
            geometry_obj = shape(feature["geometry"])
            geom_wkb = from_shape(geometry_obj, srid=4326)

            edge = EdgeModel(
                network_id=road_network.id,
                properties=feature.get("properties", {}),
                geometry=geom_wkb,
            )
            edges.append(edge)

        session.add_all(edges)

        await session.commit()
        
        return success_response(
            detail="Road network uploaded successfully"
        )
    except IntegrityError as e:
        return error_response(
            status_code=409,
            detail=f"Network `{name}` already exists"
        )
    except SQLAlchemyError as e:
        await session.rollback()
        return error_response(
            status_code=500,
            detail=f"Error occured while adding roadnetwork"
        )