from fastapi import APIRouter

from .auth.router import router as auth_router
from .customer.router import router as customer_router
from .user.router import router as user_router
from .road_network.router import router as network_router

main_router = APIRouter(prefix="/api/v1")

# Including all app routers
main_router.include_router(network_router)
main_router.include_router(customer_router)
main_router.include_router(auth_router)
main_router.include_router(user_router)