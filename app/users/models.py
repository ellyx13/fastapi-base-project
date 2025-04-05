from datetime import datetime
from typing import Literal, Optional

from auth import schemas as auth_schemas
from core.schemas import EmailStr, ObjectIdStr, PhoneStr
from pydantic import BaseModel, Field
from typing_extensions import Self


class Users(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    fullname: str
    email: EmailStr
    phone: Optional[PhoneStr] = None
    password: bytes
    type: Literal["admin", "user"]
    created_at: datetime = Field(default_factory=datetime.now)
    created_by: Optional[ObjectIdStr] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[ObjectIdStr] = None

    @classmethod
    def from_register(cls, data: auth_schemas.RegisterRequest, user_type: str, hashed_password: bytes) -> Self:
        return cls(fullname=data.fullname, email=data.email, phone=data.phone, password=hashed_password, type=user_type)
