from auth.decoractor import access_control
from core.schemas import CommonsDependencies, ObjectIdStr, PaginationParams
from fastapi import Depends
from fastapi_restful.cbv import cbv
from fastapi_restful.inferring_router import InferringRouter

from . import schemas
from .controllers import user_controllers

router = InferringRouter(
    prefix="/v1",
    tags=["v1/users"],
)


@cbv(router)
class RoutersCBV:
    """
    A class-based view for handling user-related routes in the FastAPI application.

    This class uses FastAPI's class-based view (`cbv`) approach to define various endpoints for user management,
    including retrieving user information, registering, logging in, updating, and deleting users.

    Attributes:
        commons (CommonsDependencies): Common dependencies for the request, such as the current user and user type.
    """

    commons: CommonsDependencies = Depends(CommonsDependencies)  # type: ignore

    @router.get("/users/me", status_code=200, responses={200: {"model": schemas.Response, "description": "Get users success"}})
    @access_control(public=False)
    async def get_me(self, fields: str = None):
        result = await user_controllers.get_me(commons=self.commons, fields=fields)
        return schemas.Response.model_validate(obj=result, from_attributes=True)

    @router.put("/users/me", status_code=200, responses={200: {"model": schemas.Response, "description": "Update user success"}})
    @access_control(public=False)
    async def edit_me(self, data: schemas.EditRequest):
        result = await user_controllers.edit_me(data=data, commons=self.commons)
        return schemas.Response.model_validate(obj=result, from_attributes=True)

    @router.get("/users", status_code=200, responses={200: {"model": schemas.ListResponse, "description": "Get users success"}})
    @access_control(admin=True, public=False)
    async def get_all(self, pagination: PaginationParams = Depends()):
        search_in = ["fullname", "email"]
        results = await user_controllers.get_all(
            query=pagination.query,
            search=pagination.search,
            search_in=search_in,
            page=pagination.page,
            limit=pagination.limit,
            fields_limit=pagination.fields,
            sort_by=pagination.sort_by,
            order_by=pagination.order_by,
            commons=self.commons,
        )
        if pagination.fields:
            return results
        return schemas.ListResponse.model_validate(obj=results, from_attributes=True)

    @router.get("/users/{_id}", status_code=200, responses={200: {"model": schemas.Response, "description": "Get user success"}})
    @access_control(admin=True, public=False)
    async def get_detail(self, _id: ObjectIdStr, fields: str = None):
        result = await user_controllers.get_by_id(_id=_id, fields_limit=fields, commons=self.commons)
        if fields:
            return result
        return schemas.Response.model_validate(obj=result, from_attributes=True)

    @router.put("/users/{_id}", status_code=200, responses={200: {"model": schemas.Response, "description": "Update user success"}})
    @access_control(admin=True, public=False)
    async def edit(self, _id: ObjectIdStr, data: schemas.EditRequest):
        result = await user_controllers.edit(_id=_id, data=data, commons=self.commons)
        return schemas.Response.model_validate(obj=result, from_attributes=True)

    @router.delete("/users/{_id}", status_code=204)
    @access_control(admin=True, public=False)
    async def delete(self, _id: ObjectIdStr):
        await user_controllers.soft_delete_by_id(_id=_id, commons=self.commons)
