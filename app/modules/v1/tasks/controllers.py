from core.controllers import BaseControllers
from core.schemas import CommonsDependencies
from users.controllers import user_controllers

from . import schemas
from .models import Tasks
from .services import TaskServices, task_services


class TaskControllers(BaseControllers[TaskServices]):
    def __init__(self) -> None:
        super().__init__(controller_name="tasks", service=task_services)

    async def create(self, data: schemas.CreateRequest, commons: CommonsDependencies) -> Tasks:
        await user_controllers.get_by_id(_id=commons.current_user, commons=commons)
        return await self.service.create(data=data, commons=commons)

    async def edit(self, _id: str, data: schemas.EditRequest, commons: CommonsDependencies) -> Tasks:
        await user_controllers.get_by_id(_id=commons.current_user, commons=commons)
        await self.get_by_id(_id=_id, commons=commons)
        return await self.service.edit(_id=_id, data=data, commons=commons)


task_controllers = TaskControllers()
