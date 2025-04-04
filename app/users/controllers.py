from auth import schemas as auth_schemas
from core.controllers import BaseControllers
from core.schemas import CommonsDependencies
from core.services import BaseServices

from . import schemas
from .services import user_services


class UserControllers(BaseControllers):
    def __init__(self, controller_name: str, service: BaseServices = None) -> None:
        super().__init__(controller_name, service)

    async def register(self, data: auth_schemas.RegisterRequest) -> schemas.LoginResponse:
        return await self.service.register(data=data)

    async def login(self, email: str, password: str) -> schemas.LoginResponse:
        return await self.service.login(email=email, password=password)

    async def get_me(self, commons: CommonsDependencies, fields: str = None) -> schemas.Response:
        current_user_id = self.get_current_user(commons=commons)
        result = await self.get_by_id(_id=current_user_id, fields_limit=fields, commons=commons)
        return self.schema_validate(schema=schemas.Response, data=result)

    async def edit(self, _id: str, data: schemas.EditRequest, commons: CommonsDependencies) -> schemas.Response:
        # Check if that user id exists or not
        await self.get_by_id(_id=_id, commons=commons)
        result = await self.service.edit(_id=_id, data=data, commons=commons)
        return self.schema_validate(schema=schemas.Response, data=result)


user_controllers = UserControllers(controller_name="users", service=user_services)
