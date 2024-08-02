import sys

from config import PATH_LOGS
from fastapi import FastAPI
from loguru import logger
from routers import api_routers

app = FastAPI(
    title="FastAPI Base Project",
    description="""
    This FastAPI application serves as a foundational platform for building robust API services.
    It includes:
    - User management with complete CRUD operations.
    - Task module to manage tasks with functionalities to create, update, and delete tasks.
    - Authentication and Authorization system to secure the application and ensure that users can
      only access and manage resources according to their permissions. The system supports two user
      roles: 'user' and 'admin', where 'user' has restricted access tailored to personal data and
      actions, and 'admin' enjoys full access across the platform.
    """,
    version="0.0.1",
)


app.include_router(api_routers)

logger.remove()
logger.add(
    sys.stdout,
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | {level} | <cyan>{name}</cyan>:<cyan>{function}</cyan> | <level>{message}</level>",
)
logger.add(
    PATH_LOGS,
    colorize=False,
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | {level} | <cyan>{name}</cyan>:<cyan>{function}</cyan> | <level>{message}</level>",
    rotation="100 MB",
)