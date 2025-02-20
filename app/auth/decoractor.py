import functools
from typing import Any, Callable

from core.schemas import CommonsDependencies
from utils import value

from .exceptions import AuthErrorCode
from .services import auth_services


class access_control:
    """
    A decorator class for controlling access to methods based on user roles.

    This class is used to restrict access to certain api, allowing only users with specific roles (e.g., admin) to execute them.

    Args:
        admin (bool, optional): If set to True, the decorated method will only be accessible to admin users. Defaults to False.
        public (bool, optional): If set to True, the decorated method will be accessible to all users. Defaults

    Attributes:
        admin (bool): Indicates whether the method should be restricted to admin users.
    """

    def __init__(cls, admin: bool = False, public: bool = False) -> None:
        cls.admin = admin
        cls.public = public

    async def _check_authentication_permission(self, commons: CommonsDependencies) -> None:
        try:
            token = commons.headers.get("authorization").split("Bearer ")[1]
            if not token:
                raise AuthErrorCode.Unauthorize()
            payload = await auth_services.validate_access_token(token=token)
            if not payload:
                raise AuthErrorCode.Unauthorize()
            return payload
        except Exception:
            raise AuthErrorCode.Unauthorize()

    def __call__(cls, function) -> Callable[..., Any]:
        @functools.wraps(function)
        async def decorated(*args, **kwargs):
            self_instance = kwargs.get("self")
            commons = self_instance.commons
            if cls.public is False:
                payload = await cls._check_authentication_permission(commons=commons)
                commons.current_user = payload.get("user_id")
                commons.user_type = payload.get("user_type")
                commons.is_public_api = False
            else:
                commons.is_public_api = True
            if cls.admin and commons.user_type != value.UserRoles.ADMIN.value:
                raise AuthErrorCode.Forbidden()
            return await function(*args, **kwargs)

        return decorated
