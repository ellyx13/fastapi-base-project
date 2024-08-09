from fastapi import Query, Request
from utils.value import OrderBy
from .exceptions import ErrorCode as CoreErrorCode
from typing import Annotated
from pydantic.functional_validators import AfterValidator
from datetime import datetime
from utils import validator

class PaginationParams:
    def __init__(
        self,
        request: Request,
        search: str = Query(None, description="Anything you want"),
        page: int = Query(default=1, gt=0),
        limit: int = Query(default=20, gt=0),
        fields: str = None,
        sort_by: str = Query("created_at", description="Anything you want"),
        order_by: OrderBy = Query(OrderBy.decrease.value, description="desc: Descending | asc: Ascending"),
    ):
        self.query = dict(request.query_params)
        self.search = search
        self.page = page
        self.limit = limit
        self.fields = fields
        self.sort_by = sort_by
        self.order_by = order_by
        
        
def check_object_id(value: str) -> str:
    if validator.check_object_id(_id=value):
        return value
    raise CoreErrorCode.InvalidObjectId(_id=value)
    
def check_email(value: str) -> str:
    if validator.check_email(email=value):
        return value
    raise CoreErrorCode.InvalidEmail(email=value)
    
def check_phone(value: str) -> str:
    if validator.check_phone(phone=value):
        return value
    raise CoreErrorCode.InvalidPhone(phone=value)
    
def check_date_format(value: str) -> str:
    try:
        datetime.strptime(value, "%Y-%m-%d")
        return value
    except ValueError:
        raise CoreErrorCode.InvalidDate(date=value)


ObjectIdStr = Annotated[str, AfterValidator(check_object_id)]
EmailStr = Annotated[str, AfterValidator(check_email)]
PhoneStr = Annotated[str, AfterValidator(check_phone)]
DateStr = Annotated[str, AfterValidator(check_date_format)]



