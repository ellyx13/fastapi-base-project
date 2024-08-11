from core.schemas import ObjectIdStr, PaginationParams
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
    @router.get("/users", status_code=200, responses={200: {"model": schemas.ListResponse, "description": "Get users success"}})
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
        )
        if pagination.fields:
            return results
        return schemas.ListResponse(**results)

    @router.get("/users/{_id}", status_code=200, responses={200: {"model": schemas.Response, "description": "Get users success"}})
    async def get_detail(self, _id: ObjectIdStr, fields: str = None):
        results = await user_controllers.get_by_id(_id=_id, fields_limit=fields)
        if fields:
            return results
        return schemas.Response(**results)

    @router.post("/users/register", status_code=201, responses={201: {"model": schemas.LoginResponse, "description": "Register user success"}})
    async def register(self, data: schemas.RegisterRequest):
        result = await user_controllers.register(data=data)
        return schemas.LoginResponse(**result)

    @router.post("/users/login", status_code=201, responses={201: {"model": schemas.LoginResponse, "description": "Register user success"}})
    async def login(self, data: schemas.LoginRequest):
        result = await user_controllers.login(data=data)
        return schemas.LoginResponse(**result)
