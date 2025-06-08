from fastapi import APIRouter

from .api.create_customer_api import create_customer
from .api.list_customers_api import list_customers


# Creating APIRouter instance and setting prefix, tags
router = APIRouter(prefix="/customers", tags=["Customer"])


# Adding route to the router
router.add_api_route(path="", endpoint=create_customer, methods=["POST"])

router.add_api_route(path="", endpoint=list_customers, methods=["GET"])