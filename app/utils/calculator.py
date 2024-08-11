from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta


def add_days_to_datetime(datetime_obj: datetime = None, days: int = 0) -> datetime:
    if not datetime_obj:
        datetime_obj = datetime.now()
    return datetime_obj + timedelta(days=days)


def add_months_to_datetime(datetime_obj: datetime = None, months: int = 0) -> datetime:
    if not datetime_obj:
        datetime_obj = datetime.now()
    return datetime_obj + relativedelta(months=months)
