import sys
import time
import traceback

from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware
from utils import value

from .exceptions import MiddlewareErrorCode


class LogMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request, call_next):
        start_time = time.time()
        try:
            response = await call_next(request)
        except Exception:
            exc_list = traceback.format_exception(*sys.exc_info())
            exc = "".join(exc_list)
            logger.debug(exc)
            response = MiddlewareErrorCode.SomeThingWentWrong()
        process_time = time.time() - start_time
        response.headers["X-PROCESS-TIME"] = f"{process_time:.4f}s"
        response.headers["X-REQUEST-ID"] = value.get_uuid()
        return response
