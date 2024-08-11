from fastapi import APIRouter
from modules.v1.health import routers as health_routers
from users import routers as users_routers
api_routers = APIRouter()

# Healthy check
api_routers.include_router(health_routers.router)

# Users
api_routers.include_router(users_routers.router)