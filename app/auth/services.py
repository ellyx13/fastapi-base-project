from datetime import datetime

from core.services import BaseServices
from db.base import BaseCRUD
from fastapi import Request
from jose import jwt
from utils import calculator, converter

from .config import PUBLIC_APIS, settings


class AuthenticationServices(BaseServices):
    def __init__(self, service_name: str, crud: BaseCRUD = None) -> None:
        super().__init__(service_name, crud)

    async def create_access_token(self, user_id: str, user_type: str):
        expire = calculator.add_days_to_datetime(days=settings.access_token_expire_day)
        expire_str = converter.convert_datetime_to_str(datetime_obj=expire)
        to_encode = {"user_id": user_id, "user_type": user_type, "expire": expire_str}
        encoded_jwt = jwt.encode(claims=to_encode, key=settings.secret_key, algorithm=settings.algorithm)
        return encoded_jwt

    async def validate_access_token(self, token: str) -> bool:
        try:
            token = token.split(" ")[1]
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            datetime_obj = converter.convert_str_to_datetime(datetime_str=payload["expire"])
            if datetime.now() > datetime_obj:
                return False
            if not payload.get("user_id"):
                return False
            return payload
        except Exception:
            return False

    async def check_public_api(self, request: Request) -> bool:
        api_path = request.url.path
        if api_path in PUBLIC_APIS:
            return True
        return False


authentication_services = AuthenticationServices(service_name="authentication")
