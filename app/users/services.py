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

    async def get_by_email(self, email: str, ignore_error: bool = False) -> dict:
        results = await self.get_by_field(data=email, field_name="email", ignore_error=ignore_error)
        return results[0] if results else None

    async def register(self, data: schemas.RegisterRequest) -> dict:
        # Set the user role to 'USER' by default.
        data["type"] = value.UserRoles.USER.value
        # Add the current datetime as the creation time.
        data["created_at"] = self.get_current_datetime()
        # Hash the provided password using bcrypt with a generated salt.
        data["password"] = await self.hash(value=data["password"])
        # Validate the data by creating an instance of the Users model.
        # This process helps validate fields in data according to validation rules defined in the Users model.
        # Then convert it back to a dictionary for saving.
        data_save = models.Users(**data).model_dump()
        # Save the user, ensuring the email is unique
        item = await self.save_unique(data=data_save, unique_field="email")

        # Update created_by after register to preserve query ownership logic
        data_update = {"created_by": item["_id"]}
        item = await self.update_by_id(_id=item["_id"], data=data_update)

        # Generate an access token for the user.
        item["access_token"] = await authentication_services.create_access_token(user_id=item["_id"], user_type=item["type"])
        item["token_type"] = "bearer"
        return item

    async def login(self, data: schemas.LoginRequest) -> dict:
        item = await self.get_by_email(email=data["email"], ignore_error=True)
        if not item:
            raise UserErrorCode.Unauthorize()
        # Validate the provided password against the hashed value.
        is_valid_password = await self.validate_hash(value=data["password"], hashed_value=item["password"])
        if not is_valid_password:
            raise UserErrorCode.Unauthorize()

        # Generate an access token for the user.
        item["access_token"] = await authentication_services.create_access_token(user_id=item["_id"], user_type=item["type"])
        item["token_type"] = "bearer"
        return item

    async def edit(self, _id: str, data: schemas.EditRequest, commons: CommonsDependencies) -> dict:
        data["updated_at"] = self.get_current_datetime()
        data["updated_by"] = self.get_current_user(commons=commons)
        return await self.update_by_id(_id=_id, data=data)


user_crud = BaseCRUD(database_engine=app_engine, collection="users")
user_services = UserServices(service_name="users", crud=user_crud)
