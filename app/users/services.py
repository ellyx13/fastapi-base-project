from auth.services import auth_services
from core.schemas import CommonsDependencies
from core.services import BaseServices
from db.base import BaseCRUD
from db.engine import app_engine
from utils import value

from . import schemas
from .config import settings
from .exceptions import UserErrorCode
from .models import Users


class UserServices(BaseServices[Users]):
    def __init__(self, crud: BaseCRUD = None):
        super().__init__(service_name="users", crud=crud, model=Users)

    async def get_by_email(self, email: str, ignore_error: bool = False) -> dict:
        results = await self.get_by_field(data=email, field_name="email", ignore_error=ignore_error)
        return results[0] if results else None

    async def register(self, fullname: str, email: str, password: str, phone_number: str = None) -> dict:
        data = {"fullname": fullname, "email": email, "password": password}
        if phone_number:
            data["phone_number"] = phone_number
        # Set the user role to 'USER' by default.
        data["type"] = value.UserRoles.USER.value
        # Add the current datetime as the creation time.
        data["created_at"] = self.get_current_datetime()
        # Hash the provided password using bcrypt with a generated salt.
        data["password"] = await auth_services.hash(value=data["password"])
        # Save the user, ensuring the email is unique, using the save_unique function.
        user = await self.save_unique(data=data, unique_field="email")
        # Update created_by after register to preserve query ownership logic
        data_update = {"created_by": user["_id"]}
        user = await self.update_by_id(_id=user["_id"], data=data_update)
        return user

    async def login(self, email: str, password: str) -> dict:
        user = await self.get_by_email(email=email, ignore_error=True)
        if not user:
            raise UserErrorCode.Unauthorize()
        # Validate the provided password against the hashed value.
        is_valid_password = await auth_services.validate_hash(value=password, hashed_value=user["password"])
        if not is_valid_password:
            raise UserErrorCode.Unauthorize()
        return user

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
        admin = await self.register(fullname="Admin", email=settings.default_admin_email, password=settings.default_admin_password)
        return await self.grant_admin(_id=admin["_id"])


user_crud = BaseCRUD(database_engine=app_engine, collection="users")
user_services = UserServices(crud=user_crud)
