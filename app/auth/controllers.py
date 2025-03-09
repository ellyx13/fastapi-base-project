from core.controllers import BaseControllers
from core.services import BaseServices
from users.controllers import user_controllers

from . import schemas
from .services import auth_services


class AuthControllers(BaseControllers):
    def __init__(self, controller_name: str, service: BaseServices = None) -> None:
        super().__init__(controller_name, service)

    async def register_user(self, data: schemas.RegisterRequest) -> dict:
        data = data.model_dump()
        user = await user_controllers.register(fullname=data["fullname"], email=data["email"], password=data["password"], phone_number=data.get("phone_number"))
        # Generate an access token for the user.
        user["access_token"] = await self.service.create_access_token(user_id=user["_id"], user_type=user["type"])
        user["token_type"] = "bearer"
        return user

    async def login_user(self, data: schemas.LoginRequest) -> dict:
        data = data.model_dump()
        user = await user_controllers.login(email=data["email"], password=data["password"])
        # Generate an access token for the user.
        user["access_token"] = await self.service.create_access_token(user_id=user["_id"], user_type=user["type"])
        user["token_type"] = "bearer"
        return user


auth_controllers = AuthControllers(controller_name="auth", service=auth_services)
