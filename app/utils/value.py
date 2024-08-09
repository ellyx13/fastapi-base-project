from enum import Enum

class UserRoles(Enum):
    USER = "user"
    ADMIN = "admin"
    
class OrderBy(Enum):
    DECREASE = "desc"
    ASCENDING = "asc"
    
class DataFormat(Enum):
    DATE = r"%Y-%m-%d"
    DATE_TIME = r"%Y-%m-%d %H:%M:%S"
    EMAIL_REGEX = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,10}\b"
    PHONE_REGEX = r"^\d{10}$"