from pydantic import BaseModel, ConfigDict
from core.schemas import EmailStr, PhoneStr
from datetime import datetime
from typing import Optional

class Users(BaseModel):
    fullname: str
    email: EmailStr
    phone: Optional[PhoneStr] = None
    password: bytes
    created_at: datetime