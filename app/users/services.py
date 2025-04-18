from auth import schemas as auth_schemas
from auth.services import auth_services
from core.schemas import CommonsDependencies
from core.services import BaseServices
from db.base import BaseCRUD
from db.engine import app_engine
from utils import value

from . import internal_models, schemas
from .config import settings
from .exceptions import UserErrorCode
from .models import Users


class UserServices(BaseServices[Users]):
    def __init__(self, crud: BaseCRUD = None):
        super().__init__(service_name="users", crud=crud, model=Users)

    async def get_by_email(self, email: str, ignore_error: bool = False) -> Users:
        results = await self.get_by_field(data=email, field_name="email", ignore_error=ignore_error)
        return results[0] if results else None

    async def register(self, data: auth_schemas.RegisterRequest) -> Users:
        # Set the user role to 'USER' by default.
        user_type = value.UserRoles.USER.value
        # Hash the provided password using bcrypt with a generated salt.
        hashed_password = await auth_services.hash(value=data.password)
        user_model = Users.from_register(data=data, user_type=user_type, hashed_password=hashed_password)
        # Save the user, ensuring the email is unique, using the save_unique function.
        user = await self.save_unique(data=user_model, unique_field="email")
        # Update created_by after register to preserve query ownership logic
        data_update = internal_models.UpdateCreatedBy(created_by=user.id)
        user = await self.update_by_id(_id=user.id, data=data_update)
        return user

    async def login(self, email: str, password: str) -> Users:
        user = await self.get_by_email(email=email, ignore_error=True)
        if not user:
            raise UserErrorCode.Unauthorize()
        # Validate the provided password against the hashed value.
        is_valid_password = await auth_services.validate_hash(value=password, hashed_value=user.password)
        if not is_valid_password:
            raise UserErrorCode.Unauthorize()
        return user

    async def edit(self, _id: str, data: schemas.EditRequest, commons: CommonsDependencies) -> Users:
        data = internal_models.EditWithAudit(fullname=data.fullname, phone=data.phone, updated_by=commons.current_user)
        return await self.update_by_id(_id=_id, data=data)

    async def grant_admin(self, _id: str, commons: CommonsDependencies = None):
        data = internal_models.GrantAdmin(updated_by=commons.current_user if commons else None)
        return await self.update_by_id(_id=_id, data=data)

    async def create_admin(self):
        user = await self.get_by_field(data=settings.default_admin_email, field_name="email", ignore_error=True)
        if user:
            return user
        data = auth_schemas.RegisterRequest(fullname="Admin", email=settings.default_admin_email, password=settings.default_admin_password)
        admin = await self.register(data=data)
        return await self.grant_admin(_id=admin.id)


user_crud = BaseCRUD(database_engine=app_engine, collection="users")
user_services = UserServices(crud=user_crud)
