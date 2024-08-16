import sys

from config import settings
from exceptions import CustomException
from fastapi import FastAPI, Request, Response
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from loguru import logger
from middlewares.v1.authentication import AuthenticationMiddleware
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


# Routers
app.include_router(api_routers)

# Middlewares
app.add_middleware(AuthenticationMiddleware)

# Logger
logger.remove()
logger.add(
    sys.stdout,
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | {level} | <cyan>{name}</cyan>:<cyan>{function}</cyan> | <level>{message}</level>",
)
logger.add(
    settings.logs_path,
    colorize=False,
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | {level} | <cyan>{name}</cyan>:<cyan>{function}</cyan> | <level>{message}</level>",
    rotation="100 MB",
)


@app.exception_handler(CustomException)
async def standard_exception_handler(request: Request, exc: CustomException):
    # Status code 204 (delete) and 304 (not modified) does not require response content
    if exc.status in [304, 204]:
        return Response(status_code=exc.status)
    return JSONResponse(status_code=exc.status, content={"type": exc.type, "title": exc.title, "status": exc.status, "detail": exc.detail})


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(title="FastAPI Base Project", version="0.0.1", routes=app.routes)
    openapi_schema["components"]["securitySchemes"] = {
        "Bearer Auth": {"type": "apiKey", "in": "header", "name": "Authorization", "description": "Enter: **'Bearer &lt;JWT&gt;'**, where JWT is the access token"}
    }

    # Get all routes where jwt_optional() or jwt_required
    api_router = [route for route in app.routes if isinstance(route, APIRoute)]

    for route in api_router:
        path = getattr(route, "path")
        methods = [method.lower() for method in getattr(route, "methods")]

        for method in methods:
            openapi_schema["paths"][path][method]["security"] = [{"Bearer Auth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
