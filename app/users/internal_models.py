from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field
from typing_extensions import Self
from utils.value import UserRoles

from . import schemas


class UpdateCreatedBy(BaseModel):
    created_by: str


class EditWithAudit(schemas.EditRequest):
    updated_at: datetime
    updated_by: str

    @classmethod
    def from_edit_request(cls, data: schemas.EditRequest, updated_by: str) -> Self:
        return cls(fullname=data.fullname, phone=data.phone, updated_at=datetime.now(), updated_by=updated_by)


class GrantAdmin(BaseModel):
    type: str = Field(default=UserRoles.ADMIN.value)
    updated_at: datetime = Field(default_factory=datetime.now)
    updated_by: Optional[str] = None
