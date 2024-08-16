from datetime import datetime
from typing import List, Optional

from core.schemas import EmailStr, PhoneStr
from pydantic import BaseModel, Field, field_validator

from . import config
from .exceptions import ErrorCode as UserErrorCode


class RegisterRequest(BaseModel):
    fullname: str
    email: EmailStr
    phone: Optional[PhoneStr] = None
    password: str

    @field_validator("password")
    @classmethod
    def check_the_minimum_length_of_the_password(cls, v: str) -> str:
        if len(v) < config.MINIMUM_LENGTH_OF_THE_PASSWORD:
            raise UserErrorCode.InvalidPasswordLength()
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class Response(BaseModel):
    id: str = Field(alias="_id")
    fullname: str
    email: EmailStr
    phone: Optional[PhoneStr] = None
    type: str
    created_at: datetime
    created_by: str


class ListResponse(BaseModel):
    total_items: int
    total_page: int
    records_per_page: int
    results: List[Response]


class LoginResponse(Response):
    access_token: str
    token_type: str


class EditRequest(BaseModel):
    fullname: Optional[str] = None
    phone: Optional[PhoneStr] = None
