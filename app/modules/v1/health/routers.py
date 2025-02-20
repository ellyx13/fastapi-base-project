from auth.decoractor import access_control
from core.schemas import CommonsDependencies
from fastapi import Depends
from fastapi_restful.cbv import cbv
from fastapi_restful.inferring_router import InferringRouter

router = InferringRouter(
    prefix="/v1/health",
    tags=["v1/health"],
)


@cbv(router)
class RoutersCBV:
    commons: CommonsDependencies = Depends(CommonsDependencies)  # type: ignore

    @router.get("/ping")
    @access_control(public=True)
    async def health_check(self):
        return {"ping": "pong!"}
