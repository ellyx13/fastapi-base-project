from datetime import datetime
from typing import Literal, Optional

from core.schemas import EmailStr, ObjectIdStr, PhoneStr
from pydantic import BaseModel


class Users(BaseModel):
    fullname: str
    email: EmailStr
    phone: Optional[PhoneStr] = None
    password: bytes
    type: Literal["admin", "user"]
    created_at: datetime
    created_by: Optional[ObjectIdStr] = None
