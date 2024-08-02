from fastapi_restful.cbv import cbv
from fastapi_restful.inferring_router import InferringRouter

router = InferringRouter(
    prefix="/v1/health",
    tags=["v1/health"],
)


@cbv(router)
class RoutersCBV:
    @router.get("/ping")
    async def health_check(self):
        return {"ping": "pong!"}
