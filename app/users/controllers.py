from core.controllers import BaseControllers
from core.schemas import CommonsDependencies
from core.services import BaseServices

from . import schemas
from .services import user_services


class UserControllers(BaseControllers):
    def __init__(self, controller_name: str, service: BaseServices = None) -> None:
        super().__init__(controller_name, service)

    async def register(self, fullname: str, email: str, password: str, phone_number: str = None) -> dict:
        return await self.service.register(fullname=fullname, email=email, password=password, phone_number=phone_number)

    async def login(self, email: str, password: str) -> dict:
        return await self.service.login(email=email, password=password)

    async def get_me(self, commons: CommonsDependencies, fields: str = None):
        current_user_id = self.get_current_user(commons=commons)
        return await self.get_by_id(_id=current_user_id, fields_limit=fields, commons=commons)

    async def edit(self, _id: str, data: schemas.EditRequest, commons: CommonsDependencies) -> dict:
        # Check if that user id exists or not
        await self.get_by_id(_id=_id, commons=commons)
        # Convert the Pydantic model 'data' to a dictionary, excluding any fields with None values.
        data = data.model_dump(exclude_none=True)
        return await self.service.edit(_id=_id, data=data, commons=commons)


user_controllers = UserControllers(controller_name="users", service=user_services)
