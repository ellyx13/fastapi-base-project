from auth.decoractor import access_control
from core.schemas import CommonsDependencies
from fastapi import Depends
from fastapi_restful.cbv import cbv
from fastapi_restful.inferring_router import InferringRouter

from . import schemas
from .controllers import auth_controllers

router = InferringRouter(
    prefix="/v1",
    tags=["v1/auth"],
)


@cbv(router)
class RoutersCBV:
    commons: CommonsDependencies = Depends(CommonsDependencies)  # type: ignore

    @router.post("/auth/register", status_code=201, responses={201: {"model": schemas.LoginResponse, "description": "Register user success"}})
    @access_control(public=True)
    async def register(self, data: schemas.RegisterRequest):
        result = await auth_controllers.register_user(data=data)
        return schemas.LoginResponse.model_validate(obj=result)

    @router.post("/auth/login", status_code=201, responses={201: {"model": schemas.LoginResponse, "description": "Register user success"}})
    @access_control(public=True)
    async def login(self, data: schemas.LoginRequest):
        result = await auth_controllers.login_user(data=data)
        return schemas.LoginResponse(**result)
