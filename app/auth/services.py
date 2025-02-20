from datetime import datetime

from bcrypt import checkpw, gensalt, hashpw
from core.services import BaseServices
from db.base import BaseCRUD
from jose import jwt
from utils import calculator, converter

from .config import settings


class AuthServices(BaseServices):
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

    async def hash(self, value) -> bytes:
        """
        Hashes a given string using bcrypt.

        Args:
            value (str): The string to be hashed.

        Returns:
            bytes: The hashed representation of the input string.
        """
        return hashpw(value.encode("utf8"), gensalt())

    async def validate_hash(self, value, hashed_value) -> bool:
        """
        Validates a given string against a hashed value using bcrypt.

        Args:
            value (str): The string to validate.
            hashed_value (bytes): The hashed value to compare against.

        Returns:
            bool: True if the string matches the hash, False otherwise.
        """
        if not checkpw(value.encode("utf-8"), hashed_value):
            return False
        return True


auth_services = AuthServices(service_name="auth")
