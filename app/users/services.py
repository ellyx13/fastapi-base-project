from auth.services import authentication_services
from bcrypt import checkpw, gensalt, hashpw
from core.schemas import CommonsDependencies
from core.services import BaseServices
from db.base import BaseCRUD
from db.engine import app_engine
from utils import value

from . import models, schemas
from .exceptions import ErrorCode as UserErrorCode


class UserServices(BaseServices):
    def __init__(self, service_name: str, crud: BaseCRUD = None) -> None:
        super().__init__(service_name, crud)

    async def hash(self, value) -> bytes:
        return hashpw(value.encode("utf8"), gensalt())

    async def validate_hash(self, value, hashed_value) -> bool:
        if not checkpw(value.encode("utf-8"), hashed_value):
            return False
        return True

    async def register(self, data: schemas.RegisterRequest) -> dict:
        data["type"] = value.UserRoles.USER.value
        data["created_at"] = self.get_current_datetime()
        data["password"] = await self.hash(value=data["password"])
        data_save = models.Users(**data).model_dump()
        item = await self.save_unique(data=data_save, unique_field="email")

        # Update created_by after register to preserve query ownership logic
        data_update = {"created_by": item["_id"]}
        item = await self.update_by_id(_id=item["_id"], data=data_update)

        item["access_token"] = await authentication_services.create_access_token(user_id=item["_id"], user_type=item["type"])
        item["token_type"] = "bearer"
        return item

    async def login(self, data: schemas.LoginRequest) -> dict:
        item = await self.get_by_field(data=data["email"], field_name="email", ignore_error=True)
        if not item:
            raise UserErrorCode.Unauthorize()
        is_valid_password = await self.validate_hash(value=data["password"], hashed_value=item["password"])
        if not is_valid_password:
            raise UserErrorCode.Unauthorize()
        item["access_token"] = await authentication_services.create_access_token(user_id=item["_id"], user_type=item["type"])
        item["token_type"] = "bearer"
        return item

    async def edit(self, _id: str, data: schemas.EditRequest, commons: CommonsDependencies) -> dict:
        data["updated_at"] = self.get_current_datetime()
        data["updated_by"] = self.get_current_user(commons=commons)
        return await self.update_by_id(_id=_id, data=data)


user_crud = BaseCRUD(database_engine=app_engine, collection="users")
user_services = UserServices(service_name="users", crud=user_crud)
