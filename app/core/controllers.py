from typing import Type

from core.schemas import CommonsDependencies
from pydantic import BaseModel

from .services import BaseServices

NOT_DECLARED_SERVICE = "Service must be an instance of BaseServices. Maybe the service has not been declared when creating the class Controllers"


class BaseControllers:
    """
    A base class for controllers that provides common methods for interacting with services.

    This class is designed to work with a service instance derived from `BaseServices`. It offers methods
    to perform common operations like retrieving all records, fetching records by ID or field, and soft-deleting records by ID.

    Args:
        controller_name (str): The name of the controller.
        service (BaseServices, optional): An instance of a service class derived from `BaseServices`. Defaults to None.

    Attributes:
        controller_name (str): The name of the controller.
        service (BaseServices): The service instance used for performing operations.
    """

    def __init__(self, controller_name: str, service: BaseServices = None) -> None:
        self.controller_name = controller_name
        self.service = service

    async def get_all(
        self,
        query: dict = None,
        search: str = None,
        search_in: list = None,
        page: int = 1,
        limit: int = 20,
        fields_limit: list | str = None,
        sort_by: str = "created_at",
        order_by: str = "desc",
        include_deleted: bool = False,
        commons: CommonsDependencies = None,
    ) -> dict:
        if not isinstance(self.service, BaseServices):
            raise TypeError(NOT_DECLARED_SERVICE)
        results = await self.service.get_all(
            query=query,
            search=search,
            search_in=search_in,
            page=page,
            limit=limit,
            fields_limit=fields_limit,
            sort_by=sort_by,
            order_by=order_by,
            include_deleted=include_deleted,
            commons=commons,
        )
        return results

    async def get_by_id(self, _id, fields_limit: list | str = None, ignore_error: bool = False, include_deleted: bool = False, commons: CommonsDependencies = None) -> dict:
        if not isinstance(self.service, BaseServices):
            raise TypeError(NOT_DECLARED_SERVICE)
        result = await self.service.get_by_id(_id=_id, fields_limit=fields_limit, ignore_error=ignore_error, include_deleted=include_deleted, commons=commons)
        return result

    async def get_by_field(
        self, data: str, field_name: str, fields_limit: list | str = None, ignore_error: bool = False, include_deleted: bool = False, commons: CommonsDependencies = None
    ) -> list:
        if not isinstance(self.service, BaseServices):
            raise TypeError(NOT_DECLARED_SERVICE)
        result = await self.service.get_by_field(data=data, field_name=field_name, fields_limit=fields_limit, ignore_error=ignore_error, include_deleted=include_deleted, commons=commons)
        return result

    async def soft_delete_by_id(self, _id: str, ignore_error: bool = False, commons: CommonsDependencies = None) -> dict:
        if not isinstance(self.service, BaseServices):
            raise TypeError(NOT_DECLARED_SERVICE)
        result = await self.service.soft_delete_by_id(_id=_id, ignore_error=ignore_error, commons=commons)
        return result

    def get_current_user(self, commons: CommonsDependencies):
        return commons.current_user

    def get_current_user_type(self, commons: CommonsDependencies):
        return commons.user_type

    def schema_validate(self, schema: Type[BaseModel], data: BaseModel, extra_data: dict = None) -> BaseModel:
        """
        Validates and merges data into a Pydantic schema instance.

        Args:
            schema (Type[BaseModel]): The Pydantic schema class to validate against.
            data (BaseModel): The initial data to validate.
            extra_data (dict, optional): Additional data to merge with the initial data before validation. Defaults to None.

        Returns:
            BaseModel: An instance of the provided schema class with the validated and merged data.

        Raises:
            ValidationError: If the data does not conform to the schema.
        """
        data_dict = data.model_dump()
        # Merge extra data if provided
        if extra_data:
            data_dict.update(extra_data)
        # Validate the dictionary and return a Pydantic schema instance
        return schema.model_validate(obj=data_dict)
