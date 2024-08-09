from bson import ObjectId
import re
from .value import DataFormat




def check_object_id(_id: str) -> bool:
    if ObjectId.is_valid(_id):
        return True
    return False

def check_email(email):
    pattern = DataFormat.EMAIL_REGEX.value
    if re.match(pattern, email):
        return True
    return False

def check_phone(phone):
    pattern = DataFormat.PHONE_REGEX.value
    if re.match(pattern, phone):
        return True
    return False
