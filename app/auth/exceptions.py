from core.exceptions import ErrorCode as CoreErrorCode
from exceptions import CustomException


class ErrorCode(CoreErrorCode):
    @staticmethod
    def Forbidden():
        return CustomException(type="core/warning/forbidden", status=403, title="Forbidden.", detail="You do not have permission to access this resource.")
