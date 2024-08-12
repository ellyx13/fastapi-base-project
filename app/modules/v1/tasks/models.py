from datetime import datetime
from typing import Literal, Optional

from core.schemas import ObjectIdStr
from pydantic import BaseModel


class Tasks(BaseModel):
    summary: str
    description: Optional[str] = None
    status: Literal["to_do", "in_progress", "done"]
    created_at: datetime
    created_by: ObjectIdStr
