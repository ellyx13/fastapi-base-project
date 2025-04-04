from core.exceptions import CoreErrorCode
from exceptions import CustomException


class AuthErrorCode(CoreErrorCode):
    @staticmethod
    def Forbidden():
        return CustomException(type="core/warning/forbidden", status=403, title="Forbidden.", detail="You do not have permission to access this resource.")
