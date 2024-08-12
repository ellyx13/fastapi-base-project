from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel

from app.core.schemas import ObjectIdStr


class Tasks(BaseModel):
    summary: str
    description: Optional[str] = None
    status: Literal["to_do", "in_progress", "done"]
    created_at: datetime
    created_by: ObjectIdStr
