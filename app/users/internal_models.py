from pydantic import BaseModel


class UpdateCreatedByModel(BaseModel):
    created_by: str
