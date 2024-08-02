from fastapi import APIRouter
from modules.v1.health import routers as health_routers

api_routers = APIRouter()

# Healthy check
api_routers.include_router(health_routers.router)
