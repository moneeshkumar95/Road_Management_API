from fastapi import APIRouter

from .api.login_api import login
from .api.register_api import register


# Creating APIRouter instance and setting prefix, tags
router = APIRouter(prefix="/auth", tags=["Auth"])


# Adding route to the router
router.add_api_route(path="/login", endpoint=login, methods=["POST"])

router.add_api_route(path="/register", endpoint=register, methods=["POST"])
