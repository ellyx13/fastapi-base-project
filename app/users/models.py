from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel

from app.core.schemas import EmailStr, ObjectIdStr, PhoneStr


class Users(BaseModel):
    fullname: str
    email: EmailStr
    phone: Optional[PhoneStr] = None
    password: bytes
    type: Literal["admin", "user"]
    created_at: datetime
    created_by: Optional[ObjectIdStr] = None
