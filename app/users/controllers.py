from core.services import BaseServices
from core.controllers import BaseControllers
from .services import user_services
from . import schemas

class UserControllers(BaseControllers):
    def __init__(self, controller_name: str, service: BaseServices = None) -> None:
        super().__init__(controller_name, service)

    async def register(self, data: schemas.RegisterRequest):
        data = data.model_dump()
        return await self.service.register(data=data)
        
    async def login(self, data: schemas.LoginRequest):
        data = data.model_dump()
        return await self.service.login(data=data)
        
        
user_controllers = UserControllers(controller_name="users", service=user_services)