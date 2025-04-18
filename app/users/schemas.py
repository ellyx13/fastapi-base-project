from datetime import datetime
from typing import List, Optional

from core.schemas import EmailStr, PhoneStr
from pydantic import BaseModel


class Response(BaseModel):
    id: str
    fullname: str
    email: EmailStr
    phone: Optional[PhoneStr] = None
    type: str
    created_at: datetime
    created_by: str


class ListResponse(BaseModel):
    total_items: int
    total_pages: int
    records_per_page: int
    results: List[Response]


class LoginResponse(Response):
    access_token: str
    token_type: str


class EditRequest(BaseModel):
    fullname: Optional[str] = None
    phone: Optional[PhoneStr] = None
