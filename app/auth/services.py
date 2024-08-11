from core.services import BaseServices
from db.base import BaseCRUD
from jose import jwt
from utils import calculator, converter

from .config import settings


class AuthenticationServices(BaseServices):
    def __init__(self, service_name: str, crud: BaseCRUD = None) -> None:
        super().__init__(service_name, crud)

    async def create_access_token(self, user_id: str, user_type: str):
        expire = calculator.add_days_to_datetime(days=settings.access_token_expire_day)
        expire_str = converter.convert_datetime_to_str(datetime_obj=expire)
        to_encode = {"user_id": user_id, "user_type": user_type, "expire": expire_str}
        encoded_jwt = jwt.encode(claims=to_encode, key=settings.secret_key, algorithm=settings.algorithm)
        return encoded_jwt


authentication_services = AuthenticationServices(service_name="authentication")
