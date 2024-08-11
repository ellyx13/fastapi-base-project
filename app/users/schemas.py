from pydantic import BaseModel, field_validator, Field
from core.schemas import EmailStr, PhoneStr
from . import config
from .exceptions import ErrorCode as UserErrorCode
from typing import Optional, List
from datetime import datetime

class RegisterRequest(BaseModel):
    fullname: str
    email: EmailStr
    phone: Optional[PhoneStr] = None
    password: str
    
    @field_validator('password')
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
    created_at: datetime
    
class ListResponse(BaseModel):
    total_items: int
    total_page: int
    records_per_page: int
    results: List[Response]