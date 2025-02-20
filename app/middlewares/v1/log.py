import time

from starlette.middleware.base import BaseHTTPMiddleware
from utils import value


class LogMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-PROCESS-TIME"] = f"{process_time:.4f}s"
        response.headers["X-REQUEST-ID"] = value.get_uuid()
        return response
