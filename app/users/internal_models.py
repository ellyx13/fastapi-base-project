from datetime import datetime

from pydantic import BaseModel
from typing_extensions import Self

from . import schemas


class UpdateCreatedByModel(BaseModel):
    created_by: str


class EditRequestWithAudit(schemas.EditRequest):
    updated_at: datetime
    updated_by: str

    @classmethod
    def from_edit_request(cls, data: schemas.EditRequest, updated_by: str) -> Self:
        return cls(fullname=data.fullname, phone=data.phone, updated_at=datetime.now(), updated_by=updated_by)
