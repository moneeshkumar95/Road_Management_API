from typing import Optional, Union
from datetime import datetime
import json
from tempfile import NamedTemporaryFile

from fastapi import Depends, Query, status
from fastapi.responses import JSONResponse
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import select
from shapely.geometry import mapping
from geoalchemy2.shape import to_shape

from ..models import RoadNetworkModel, EdgeModel
from src.database import get_db
from src.global_utils import error_response
from src.apps.user.models import UserModel
from src.apps.auth.utils import get_current_user


async def get_road_network_edges(
    name: str = Query(...),
    timestamp: Optional[datetime] = Query(None),
    version: Optional[float] = Query(None),
    export: Optional[bool] = Query(False),
    session: AsyncSession = Depends(get_db),
    user: UserModel = Depends(get_current_user),
) -> JSONResponse | JSONResponse:
    """
    Fetches edges of a specified road network optional filtered by either timestamp or version.

    Args:
        name (str): Name of the road network.
        timestamp (Optional[datetime]): Filter to get the latest network created on or before this timestamp.
        version (Optional[float]): Filter to get the network of a specific version.
        export (Optional[bool]): If True, returns the result as a downloadable GeoJSON file. Defaults to False.

    Returns:
        JSONResponse or FileResponse:
        - If `export` is False (default): returns a GeoJSON FeatureCollection of edges.
        - If `export` is True: returns the GeoJSON as a downloadable `.geojson` file.
        - On error: returns a JSON error response with the appropriate status code.
    """
    try:
        filters = [
            RoadNetworkModel.name == name,
            RoadNetworkModel.customer_id == user.customer_id
        ]
        
        if timestamp and version:
            return error_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You can filter by either 'timestamp' or 'version', not both. Please provide only one."
            )

        if timestamp:
            filters.append(RoadNetworkModel.created_at <= timestamp)

        if version:
            filters.append(RoadNetworkModel.version == version)

        road_network_query = (
            select(RoadNetworkModel)
            .where(*filters)
            .order_by(RoadNetworkModel.version.desc())
            .limit(1)
        )
        road_network_result = await session.execute(road_network_query)
        road_network = road_network_result.scalars().first()

        if not road_network:
            return error_response(
                status_code=404, 
                detail="Road network not found"
            )
        
        edges_query = (
            select(EdgeModel)
            .where(EdgeModel.network_id == road_network.id)
        )

        edges_result = await session.execute(edges_query)
        edges = edges_result.scalars().all()

        geojson = {
            "type": "FeatureCollection",
            "features": []
        }

        for edge in edges:
            geometry = to_shape(edge.geometry)
            geojson["features"].append(
                {
                    "type": "Feature",
                    "geometry": mapping(geometry),
                    "properties": edge.properties
                }
            )

        if export:
            with NamedTemporaryFile(delete=False, suffix=".geojson", mode='w', encoding='utf-8') as tmpfile:
                json.dump(geojson, tmpfile)
                tmpfile.flush()
                return FileResponse(
                    path=tmpfile.name,
                    media_type="application/geo+json",
                    filename=f"{name}_v{road_network.version}.geojson"
                )

        return geojson
    except SQLAlchemyError as e:
        await session.rollback()
        return error_response(
            status_code=500,
            detail=f"Error occured while fetching edges"
        )