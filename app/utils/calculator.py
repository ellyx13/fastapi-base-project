from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta


def add_days_to_datetime(datetime_obj: datetime = None, days: int = 0) -> datetime:
    """
    Adds a specified number of days to a given datetime object.

    Args:
        datetime_obj (datetime): The initial datetime object to which days will be added.
                                 If None, the current datetime is used.
        days (int): The number of days to add to the datetime object. Defaults to 0.

    Returns:
        new_datetime (datetime): A new datetime object with the specified number of days added.
    """

    if not datetime_obj:
        datetime_obj = datetime.now()
    return datetime_obj + timedelta(days=days)


def add_months_to_datetime(datetime_obj: datetime = None, months: int = 0) -> datetime:
    """
    Adds a specified number of months to a given datetime object.

    Args:
        datetime_obj (datetime): The initial datetime object to which months will be added.
                                 If None, the current datetime is used.
        months (int): The number of months to add to the datetime object. Defaults to 0.

    Returns:
        new_datetime (datetime): A new datetime object with the specified number of months added.
    """
    if not datetime_obj:
        datetime_obj = datetime.now()
    return datetime_obj + relativedelta(months=months)
