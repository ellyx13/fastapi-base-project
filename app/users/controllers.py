from auth import schemas as auth_schemas
from core.controllers import BaseControllers
from core.schemas import CommonsDependencies

from . import schemas
from .models import Users
from .services import UserServices, user_services


class UserControllers(BaseControllers[UserServices]):
    def __init__(self) -> None:
        super().__init__(controller_name="users", service=user_services)

    async def register(self, data: auth_schemas.RegisterRequest) -> Users:
        return await self.service.register(data=data)

    async def login(self, email: str, password: str) -> Users:
        return await self.service.login(email=email, password=password)

    async def get_me(self, commons: CommonsDependencies, fields: str = None) -> Users:
        return await self.get_by_id(_id=commons.current_user, fields_limit=fields, commons=commons)

    async def edit(self, _id: str, data: schemas.EditRequest, commons: CommonsDependencies) -> Users:
        # Check if that user id exists or not
        await self.get_by_id(_id=_id, commons=commons)
        return await self.service.edit(_id=_id, data=data, commons=commons)

    async def edit_me(self, data: schemas.EditRequest, commons: CommonsDependencies) -> Users:
        return await self.edit(_id=commons.current_user, data=data, commons=commons)


user_controllers = UserControllers()
