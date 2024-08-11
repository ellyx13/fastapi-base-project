import functools
from typing import Any, Callable

from utils import value

from .exceptions import ErrorCode as AuthErrorCode


class access_control:
    def __init__(cls, admin: bool = False) -> None:
        cls.admin = admin

    def __call__(cls, function) -> Callable[..., Any]:
        @functools.wraps(function)
        async def decorated(*args, **kwargs):
            self_instance = kwargs.get("self")
            commons = self_instance.commons
            if commons.is_public_api:
                return await function(*args, **kwargs)
            if cls.admin and commons.user_type != value.UserRoles.ADMIN.value:
                raise AuthErrorCode.Forbidden()
            return await function(*args, **kwargs)

        return decorated
