from datetime import datetime

from pydantic import Field

from . import schemas


class EditWithAudit(schemas.EditRequest):
    updated_at: datetime = Field(default_factory=datetime.now)
    updated_by: str
