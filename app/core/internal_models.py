from datetime import datetime

from pydantic import BaseModel, Field


class SoftDelete(BaseModel):
    deleted_at: datetime = Field(default_factory=datetime.now)
    deleted_by: str
