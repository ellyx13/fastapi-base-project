from auth.services import authentication_services
from starlette.middleware.base import BaseHTTPMiddleware

from .exceptions import ErrorCode as MiddlewareErrorCode


class AuthenticationMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request, call_next):
        is_public_api = await authentication_services.check_public_api(request=request)
        if is_public_api:
            request.state.payload = {"is_public_api": True}
        else:
            token = request.headers.get("Authorization")
            if not token:
                return MiddlewareErrorCode.Unauthorize()
            payload = await authentication_services.validate_access_token(token=token)
            if not payload:
                return MiddlewareErrorCode.Unauthorize()
            request.state.payload = payload

        response = await call_next(request)
        return response
