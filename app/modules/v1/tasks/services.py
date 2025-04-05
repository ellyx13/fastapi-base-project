from core.schemas import CommonsDependencies
from core.services import BaseServices
from db.base import BaseCRUD
from db.engine import app_engine

from . import internal_models, schemas
from .models import Tasks


class TaskServices(BaseServices[Tasks]):
    def __init__(self, crud: BaseCRUD = None):
        super().__init__(service_name="tasks", crud=crud, model=Tasks)

    async def create(self, data: schemas.CreateRequest, commons: CommonsDependencies) -> Tasks:
        created_by = self.get_current_user(commons=commons)
        task = Tasks(summary=data.summary, description=data.description, status="to_do", created_by=created_by)
        return await self.save(data=task)

    async def edit(self, _id: str, data: schemas.EditRequest, commons: CommonsDependencies) -> Tasks:
        updated_by = self.get_current_user(commons=commons)
        data = internal_models.EditWithAudit(summary=data.summary, description=data.description, updated_by=updated_by)
        return await self.update_by_id(_id=_id, data=data)


task_crud = BaseCRUD(database_engine=app_engine, collection="tasks")
task_services = TaskServices(crud=task_crud)
