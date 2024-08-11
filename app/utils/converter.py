from datetime import datetime

from utils import value


def convert_datetime_to_str(datetime_obj: datetime) -> str:
    """
    Converts a datetime object to a string using the format "%Y-%m-%d %H:%M:%S".

    Args:
        datetime_obj (datetime): The datetime object to be converted to a string.

    Returns:
        formatted_datetime (str): The datetime object as a formatted string in the format "%Y-%m-%d %H:%M:%S".
    """
    return datetime_obj.strftime(value.DataFormat.DATE_TIME.value)


def convert_str_to_datetime(datetime_str: str) -> datetime:
    """
    Converts a datetime string in the format "%Y-%m-%d %H:%M:%S" to a datetime object.

    Args:
        datetime_str (str): The datetime string to be converted.

    Returns:
        datetime_obj (datetime): The corresponding datetime object.

    """
    return datetime.strptime(datetime_str, value.DataFormat.DATE_TIME.value)
