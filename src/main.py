from fastapi import FastAPI

from .apps.router_registry import main_router
from .settings import app_settings
from .setup import create_application

app: FastAPI = create_application(app_settings=app_settings, router=main_router)
