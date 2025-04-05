from datetime import datetime
from typing import Literal, Optional

from core.schemas import ObjectIdStr
from pydantic import BaseModel, Field


class Tasks(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    summary: str
    description: Optional[str] = None
    status: Literal["to_do", "in_progress", "done"]
    created_at: datetime = Field(default_factory=datetime.now)
    created_by: ObjectIdStr
