from core.exceptions import ErrorCode as CoreErrorCode
from exceptions import CustomException


class ErrorCode(CoreErrorCode):
    @staticmethod
    def InvalidPasswordLength():
        return CustomException(type="users/info/invalid-password-length", status=400, title="Invalid password length.", detail="The password must be at least 8 characters long.")
