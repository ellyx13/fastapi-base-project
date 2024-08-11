from datetime import datetime

from utils import value


def convert_datetime_to_str(datetime_obj: datetime) -> str:
    return datetime_obj.strftime(value.DataFormat.DATE_TIME.value)
