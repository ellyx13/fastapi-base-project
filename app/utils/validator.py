import re

from bson import ObjectId

from .value import DataFormat


def check_object_id(_id: str) -> bool:
    """
    Checks if a given string is a valid ObjectId.

    Args:
        _id (str): The string to check.

    Returns:
        is_valid (bool): True if the string is a valid ObjectId, False otherwise.
    """
    if ObjectId.is_valid(_id):
        return True
    return False


def check_email(email):
    """
    Checks if a given string is a valid email address based on the defined regex pattern.

    Args:
        email (str): The email address to check.

    Returns:
        is_valid (bool): True if the email matches the regex pattern, False otherwise.
    """
    pattern = DataFormat.EMAIL_REGEX.value
    if re.match(pattern, email):
        return True
    return False


def check_phone(phone):
    """
    Checks if a given string is a valid phone number based on the defined regex pattern.

    Args:
        phone (str): The phone number to check.

    Returns:
        is_valid (bool): True if the phone number matches the regex pattern, False otherwise.
    """
    pattern = DataFormat.PHONE_REGEX.value
    if re.match(pattern, phone):
        return True
    return False
