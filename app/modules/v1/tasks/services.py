from core.schemas import CommonsDependencies
from core.services import BaseServices
from db.base import BaseCRUD
from db.engine import app_engine

from . import models, schemas


class TaskServices(BaseServices):
    def __init__(self, service_name: str, crud: BaseCRUD = None) -> None:
        super().__init__(service_name, crud)

    async def create(self, data: schemas.CreateRequest, commons: CommonsDependencies) -> dict:
        data["status"] = "to_do"
        data["created_by"] = self.get_current_user(commons=commons)
        data["created_at"] = self.get_current_datetime()
        data_save = models.Tasks(**data).model_dump()
        return await self.save(data=data_save)

    async def edit(self, _id: str, data: schemas.EditRequest, commons: CommonsDependencies) -> dict:
        data["updated_by"] = self.get_current_user(commons=commons)
        data["updated_at"] = self.get_current_datetime()
        return await self.update_by_id(_id=_id, data=data)


task_crud = BaseCRUD(database_engine=app_engine, collection="tasks")
task_services = TaskServices(service_name="tasks", crud=task_crud)
