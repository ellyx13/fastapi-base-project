from auth.services import authentication_services
from core.schemas import CommonsDependencies
from core.services import BaseServices
from db.base import BaseCRUD
from db.engine import app_engine
from utils import value
from .config import settings
from . import models, schemas
from .exceptions import ErrorCode as UserErrorCode


class UserServices(BaseServices):
    def __init__(self, service_name: str, crud: BaseCRUD = None) -> None:
        super().__init__(service_name, crud)

    async def get_by_email(self, email: str, ignore_error: bool = False) -> dict:
        results = await self.get_by_field(data=email, field_name="email", ignore_error=ignore_error)
        return results[0] if results else None

    async def register(self, data: schemas.RegisterRequest) -> dict:
        # Set the user role to 'USER' by default.
        data["type"] = value.UserRoles.USER.value
        # Add the current datetime as the creation time.
        data["created_at"] = self.get_current_datetime()
        # Hash the provided password using bcrypt with a generated salt.
        data["password"] = authentication_services.hash(value=data["password"])
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
        is_valid_password = authentication_services.validate_hash(value=data["password"], hashed_value=item["password"])
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
    
    async def grant_admin(self, _id: str, commons: CommonsDependencies = None):
        data = {}
        data["type"] = value.UserRoles.ADMIN.value
        data["updated_at"] = self.get_current_datetime()
        data["updated_by"] = self.get_current_user(commons=commons)
        return await self.update_by_id(_id=_id, data=data)
    
    async def create_admin(self):
        user = await self.get_by_field(data=settings.default_admin_email, field_name="email", ignore_error=True)
        if user:
            return user
        data = {}
        data["fullname"] = "Admin"
        data["email"] = settings.default_admin_email
        data["password"] = settings.default_admin_password
        admin = await self.register(data=data)
        return await self.grant_admin(_id=admin["_id"])


user_crud = BaseCRUD(database_engine=app_engine, collection="users")
user_services = UserServices(service_name="users", crud=user_crud)
