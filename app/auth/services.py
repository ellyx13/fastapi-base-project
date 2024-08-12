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

    async def create_access_token(self, user_id: str, user_type: str) -> dict:
        """
        Creates a JWT access token for the specified user.

        Args:
            user_id (str): The ID of the user for whom the token is being created.
            user_type (str): The type of the user (e.g., admin, customer).

        Returns:
            str: The encoded JWT access token.
        """
        expire = calculator.add_days_to_datetime(days=settings.access_token_expire_day)
        expire_str = converter.convert_datetime_to_str(datetime_obj=expire)
        to_encode = {"user_id": user_id, "user_type": user_type, "expire": expire_str}
        encoded_jwt = jwt.encode(claims=to_encode, key=settings.secret_key, algorithm=settings.algorithm)
        return encoded_jwt

    async def validate_access_token(self, token: str) -> bool:
        """
        Validates a JWT access token.

        Args:
            token (str): The JWT access token to be validated.

        Returns:
            bool: True if the token is valid and not expired, False otherwise.

        """
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
        """
        Checks if the API being accessed is a public API.

        Args:
            request (Request): The FastAPI request object.

        Returns:
            bool: True if the API path is listed as a public API, False otherwise.

        """
        api_path = request.url.path
        if api_path in PUBLIC_APIS:
            return True
        return False


authentication_services = AuthenticationServices(service_name="authentication")
