from core.services import BaseServices
from db.base import BaseCRUD
from db.engine import app_engine
from . import schemas, models
from bcrypt import gensalt, hashpw, checkpw
from .exceptions import ErrorCode as UserErrorCode

class UserServices(BaseServices):
    def __init__(self, service_name: str, crud: BaseCRUD = None) -> None:
        super().__init__(service_name, crud)
        
    async def hash(self, value) -> bytes:
        return hashpw(value.encode('utf8'), gensalt())

    async def validate_hash(self, value, hashed_value) -> bool:
        if not checkpw(value.encode('utf-8'), hashed_value):
            return False
        return True
        
    async def register(self, data: schemas.RegisterRequest) -> dict:
        data['created_at'] = self.get_current_datetime()
        data['password'] = await self.hash(value=data['password'])
        data_save = models.Users(**data).model_dump()
        result = await self.save_unique(data=data_save, unique_field='email')
        return result
        
    async def login(self, data: schemas.LoginRequest) -> dict:
        item = await self.get_by_field(data=data['email'], field_name='email', ignore_error=True)
        if not item:
            raise UserErrorCode.Unauthorize()
        is_valid_password = await self.validate_hash(value=data['password'], hashed_value=item['password'])
        if not is_valid_password:
            raise UserErrorCode.Unauthorize()
        return item
        
user_crud = BaseCRUD(database_engine=app_engine, collection="users")
user_services = UserServices(service_name="users", crud=user_crud)
        
