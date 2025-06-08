from fastapi import APIRouter

from .api.create_road_network_api import create_road_network
from .api.update_road_network_api import update_road_network
from .api.get_road_network_edges_api import get_road_network_edges
from .api.list_road_networks_api import list_road_networks

# Creating APIRouter instance and setting prefix, tags
router = APIRouter(prefix="/road-network", tags=["Road Network"])


# Adding route to the router
router.add_api_route(path="", endpoint=create_road_network, methods=["POST"])

router.add_api_route(path="", endpoint=update_road_network, methods=["PUT"])

router.add_api_route(path="", endpoint=list_road_networks, methods=["GET"])

router.add_api_route(path="/edges", endpoint=get_road_network_edges, methods=["GET"])