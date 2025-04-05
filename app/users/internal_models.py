from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field
from utils.value import UserRoles

from . import schemas


class UpdateCreatedBy(BaseModel):
    created_by: str


class EditWithAudit(schemas.EditRequest):
    updated_at: datetime = Field(default_factory=datetime.now)
    updated_by: str


class GrantAdmin(BaseModel):
    type: str = Field(default=UserRoles.ADMIN.value)
    updated_at: datetime = Field(default_factory=datetime.now)
    updated_by: Optional[str] = None
