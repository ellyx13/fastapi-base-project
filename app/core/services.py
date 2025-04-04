from datetime import datetime
from typing import Generic, List, Type, TypeVar, Union

from config import settings as root_settings
from db.base import BaseCRUD
from pydantic import BaseModel
from pydantic._internal._model_construction import ModelMetaclass
from utils import value

from .config import settings
from .exceptions import CoreErrorCode
from .schemas import CommonsDependencies

TModel = TypeVar("TModel", bound=BaseModel)


# This class is used to define the structure of the response when retrieving all records. Why I put class here?
# Because it is a generic class that can be used to define the structure of the response for any model.
class GetAllModel(BaseModel):
    total_items: int
    total_pages: int
    records_per_page: int
    results: List[BaseModel]


class BaseServices(Generic[TModel]):
    """
    A base service class that provides common CRUD operations and utilities for interacting with the database.

    This class is designed to work with a CRUD instance derived from `BaseCRUD` and offers methods
    for performing various database operations such as retrieving records by ID or field, saving and updating records,
    and handling soft and hard deletions.

    Args:
        service_name (str): The name of the service.
        crud (BaseCRUD, optional): An instance of a CRUD class derived from `BaseCRUD`. Defaults to None.

    Attributes:
        crud (BaseCRUD): The CRUD instance used for database operations.
        service_name (str): The name of the service.

    """

    def __init__(self, service_name: str, crud: BaseCRUD = None, model: Type[TModel] = None) -> None:
        self.service_name = service_name
        self.ownership_field = settings.ownership_field
        if crud and root_settings.is_production() and isinstance(crud, BaseCRUD) is False:
            raise ValueError(f"The 'crud' attribute must be a BaseCRUD instance for {self.service_name} service.")
        if model and isinstance(model, ModelMetaclass) is False:
            raise ValueError(f"The 'model' attribute must be a Pydantic Model for {self.service_name} service.")
        self.crud = crud
        self.model = model

    def ensure_crud_provided(self) -> None:
        if self.crud is None:
            raise ValueError(f"The 'crud' attribute must be provided for {self.service_name} service.")

    def get_current_datetime(self) -> datetime:
        """
        Returns:
            datetime: ISO 8601 Date Format: YYYY-MM-DD HH:MM:SS.sssZ
        """
        return datetime.now()

    def get_current_user(self, commons: CommonsDependencies):
        """
        Retrieves the current user from the provided common dependencies.

        Args:
            commons (CommonsDependencies): The common dependencies containing the current user information.

        Returns:
            str: The ID of the current user.

        """
        return commons.current_user if commons else None

    def get_current_user_type(self, commons: CommonsDependencies):
        """
        Retrieves the type of the current user from the provided common dependencies.

        Args:
            commons (CommonsDependencies): The common dependencies containing the user type information.

        Returns:
            str: The type of the current user (e.g., admin, customer).

        """
        return commons.user_type if commons else None

    def build_ownership_query(self, commons: CommonsDependencies = None) -> dict | None:
        """
        Builds a query to filter records based on the ownership of the current user.

        Args:
            commons (CommonsDependencies, optional): The common dependencies containing the current user and user type.

        Returns:
            dict | None: A dictionary representing the ownership query, or None if no ownership query is needed.

        """
        if not commons:
            return None
        current_user_id = self.get_current_user(commons=commons)
        if not current_user_id:
            return None

        current_user_type = self.get_current_user_type(commons=commons)
        if current_user_type == value.UserRoles.ADMIN.value:
            return None

        query = {}
        if self.ownership_field:
            query[self.ownership_field] = current_user_id
        return query

    async def _validate_model(self, data: list | dict) -> list[TModel] | TModel:
        """
        Validates the provided data against the model.

        Args:
            data (list | dict): The data to validate.

        Returns:
            list | TModel: The validated data.

        Raises:
            ValueError: If the data is not valid according to the model.

        """
        if isinstance(data, list):
            print(11111111)
            return [self.model.model_validate(item) for item in data]
        return self.model.model_validate(data)

    async def get_by_id(self, _id: str, fields_limit: list | str = None, ignore_error: bool = False, include_deleted: bool = False, commons: CommonsDependencies = None) -> TModel:
        """
        Retrieves a record by its ID.

        Args:
            _id (str): The ID of the record to retrieve.
            fields_limit (list | str, optional): Fields to include in the response. Defaults to None.
            ignore_error (bool, optional): Whether to ignore errors if the record is not found. Defaults to False.
            include_deleted (bool, optional): Whether to include soft-deleted records. Defaults to False.
            commons (CommonsDependencies, optional): Common dependencies for the request. Defaults to None.

        Returns:
            TModel: The retrieved record.

        Raises:
            CoreErrorCode.NotFound: If the record is not found and `ignore_error` is False.

        """
        self.ensure_crud_provided()
        query = {}
        if not include_deleted:
            query.update({"deleted_at": None})

        # Enhance owner user query
        ownership_query = self.build_ownership_query(commons=commons)
        if ownership_query:
            query.update(ownership_query)

        item = await self.crud.get_by_id(_id=_id, fields_limit=fields_limit, query=query)
        if not item and not ignore_error:
            raise CoreErrorCode.NotFound(service_name=self.service_name, item=_id)
        return self.model.model_validate(item)

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
    ) -> GetAllModel:
        """
        Retrieves all records based on the provided query parameters.

        Args:
            query (dict, optional): A dictionary containing filter conditions. Defaults to None.
            search (str, optional): A search string to apply across specified fields. Defaults to None.
            search_in (list, optional): A list of fields to search within. Defaults to None.
            page (int, optional): The page number for pagination. Defaults to 1.
            limit (int, optional): The number of records to retrieve per page. Defaults to 20.
            fields_limit (list | str, optional): Fields to include in the response. Defaults to None.
            sort_by (str, optional): The field to sort the results by. Defaults to "created_at".
            order_by (str, optional): The sort order, either "asc" or "desc". Defaults to "desc".
            include_deleted (bool, optional): Whether to include soft-deleted records. Defaults to False.
            commons (CommonsDependencies, optional): Common dependencies for the request. Defaults to None.

        Returns:
            GetAllModel: A model containing the total number of items, total pages, and the results.

        """
        self.ensure_crud_provided()
        if not query:
            query = {}
        if not include_deleted:
            query.update({"deleted_at": None})

        # Enhance owner user query
        ownership_query = self.build_ownership_query(commons=commons)
        if ownership_query:
            query.update(ownership_query)

        results = await self.crud.get_all(query=query, search=search, search_in=search_in, page=page, limit=limit, fields_limit=fields_limit, sort_by=sort_by, order_by=order_by)
        results["results"] = await self._validate_model(data=results["results"])
        return GetAllModel(total_items=results["total_items"], total_pages=results["total_pages"], records_per_page=results["records_per_page"], results=results["results"])

    async def get_by_field(
        self, data: str, field_name: str, fields_limit: list | str = None, ignore_error: bool = False, include_deleted: bool = False, commons: CommonsDependencies = None
    ) -> list | None:
        """
        Retrieves a record by a specific field value.

        Args:
            data (str): The value to search for within the specified field.
            field_name (str): The name of the field to search within.
            fields_limit (list | str, optional): Fields to include in the response. Defaults to None.
            ignore_error (bool, optional): Whether to ignore errors if the record is not found. Defaults to False.
            include_deleted (bool, optional): Whether to include soft-deleted records. Defaults to False.
            commons (CommonsDependencies, optional): Common dependencies for the request. Defaults to None.

        Returns:
            list: A list representing the retrieved record.

        Raises:
            CoreErrorCode.NotFound: If the record is not found and `ignore_error` is False.

        """
        self.ensure_crud_provided()
        query = {}
        if not include_deleted:
            query.update({"deleted_at": None})

        # Enhance owner user query
        ownership_query = self.build_ownership_query(commons=commons)
        if ownership_query:
            query.update(ownership_query)

        items = await self.crud.get_by_field(data=data, field_name=field_name, fields_limit=fields_limit, query=query)
        if not items:
            if not ignore_error:
                raise CoreErrorCode.NotFound(service_name=self.service_name, item=data)
            return None
        return await self._validate_model(data=items)

    async def _check_modified(self, old_data: TModel, new_data: TModel, ignore_error: bool) -> bool:
        """
        Checks if the new data is different from the old data.
        Args:
            old_data (TModel): The old data to compare against.
            new_data (TModel): The new data to compare.
            ignore_error (bool): Whether to ignore errors if the data is not modified.
        Returns:
            bool: True if the data is modified, False otherwise.
        """

        for field in new_data.model_fields:
            if field in ["updated_at", "updated_by"]:
                continue

            new_val = getattr(new_data, field, None)
            old_val = getattr(old_data, field, None)

            if new_val != old_val:
                return True

        if ignore_error:
            return False
        raise CoreErrorCode.NotModified(service_name=self.service_name)

    async def _check_unique(self, data: dict, unique_field: str | list, ignore_error: bool = False) -> bool:
        """
        Checks if a field or set of fields is unique within the database.

        Args:
            data (dict): The data to check for uniqueness.
            unique_field (str | list): The field or fields to check for uniqueness.
            ignore_error (bool, optional): Whether to ignore errors if a conflict is found. Defaults to False.

        Returns:
            bool: True if the field or fields are unique, False otherwise.

        Raises:
            CoreErrorCode.Conflict: If a conflict is detected and `ignore_error` is False.

        """
        unique_field = [unique_field] if type(unique_field) is str else unique_field
        query = {}
        for field in unique_field:
            if data.get(field):
                query[field] = data[field]
        if not query:
            return False
        total_items = await self.crud.count_documents(query=query)
        if total_items == 0:
            return True
        if ignore_error:
            return False
        first_item = next(iter(query.values()))
        raise CoreErrorCode.Conflict(service_name=self.service_name, item=first_item)

    async def save(self, data: TModel) -> TModel:
        """
        Saves a new record to the database.

        Args:
            data (TModel): The data to be saved.

        Returns:
            TModel: The saved record, retrieved by its ID.
        """
        self.ensure_crud_provided()
        # Validate and process the data using the provided model.
        data_save = data.model_dump(exclude_none=True)
        item = await self.crud.save(data=data_save)
        result = await self.get_by_id(_id=item)
        return result

    async def save_many(self, data: list[TModel]) -> list[TModel]:
        """
        Saves multiple records to the database.

        Args:
            data (list[TModel]): A list of dictionaries, each representing a record to be saved.

        Returns:
            list[TModel]: A list of saved records, each retrieved by its ID.

        """
        self.ensure_crud_provided()
        # Validate and process each record using the provided model.
        data_save = [item.model_dump(exclude_none=True) for item in data]
        items = await self.crud.save_many(data=data_save)
        results = []
        for item_id in items:
            item = await self.get_by_id(_id=item_id)
            results.append(item)
        return results

    async def save_unique(self, data: TModel, unique_field: Union[str, list[str]], ignore_error: bool = False) -> Union[bool, dict]:
        """
        Saves a new record to the database, ensuring that specified fields are unique.

        Args:
            data (TModel): The model instance to be saved.
            unique_field (str | list): The field(s) that must be unique in the database.
            ignore_error (bool): Whether to ignore errors if a conflict is found.

        Returns:
            dict | bool: The saved record or False if ignored.

        Raises:
            CoreErrorCode.Conflict: If a conflict is detected and ignore_error is False.
        """
        self.ensure_crud_provided()

        data_dict = data.model_dump(exclude_none=True)
        item = await self.crud.save_unique(data=data_dict, unique_field=unique_field)

        if not item:
            if ignore_error:
                return False
            if isinstance(unique_field, list):
                unique_value = getattr(data, unique_field[0])
            else:
                unique_value = getattr(data, unique_field)
            raise CoreErrorCode.Conflict(service_name=self.service_name, item=unique_value)

        return await self.get_by_id(_id=item)

    async def update_by_id(
        self,
        _id: str,
        data: TModel,
        unique_field: str | list = None,
        check_modified: bool = True,
        ignore_error: bool = False,
        include_deleted: bool = False,
        commons: CommonsDependencies = None,
    ) -> TModel | None:
        """
        Updates a record by its ID.

        Args:
            _id (str): The ID of the record to update.
            data (TModel): The new data to update the record with.
            unique_field (str | list, optional): The field or fields that must be unique in the database. Defaults to None.
            check_modified (bool, optional): Whether to check if the data has been modified before updating. Defaults to True.
            ignore_error (bool, optional): Whether to ignore errors if the record is not found or not modified. Defaults to False.
            include_deleted (bool, optional): Whether to include soft-deleted records in the update. Defaults to False.
            commons (CommonsDependencies, optional): Common dependencies for the request. Defaults to None.

        Returns:
            TModel | None: The updated record, or None if `ignore_error` is True and the record is not found.

        Raises:
            CoreErrorCode.NotFound: If the record is not found and `ignore_error` is False.
            CoreErrorCode.NotModified: If the record is not modified and `ignore_error` is False.
            CoreErrorCode.Conflict: If a conflict is detected in the unique fields and `ignore_error` is False.

        """
        self.ensure_crud_provided()
        item = await self.get_by_id(_id=_id, ignore_error=ignore_error, include_deleted=include_deleted, commons=commons)
        if not item and ignore_error:
            return None
        if check_modified:
            await self._check_modified(old_data=item, new_data=data, ignore_error=ignore_error)
        if unique_field:
            await self._check_unique(data=data, unique_field=unique_field, ignore_error=ignore_error)
        data_dict = data.model_dump(exclude_none=True)
        await self.crud.update_by_id(_id=_id, data=data_dict)
        result = await self.get_by_id(_id=_id, ignore_error=ignore_error, include_deleted=True)
        return result

    async def hard_delete_by_id(self, _id: str, ignore_error: bool = False, include_deleted: bool = False, commons: CommonsDependencies = None) -> bool:
        """
        Permanently deletes a record by its ID.

        Args:
            _id (str): The ID of the record to delete.
            ignore_error (bool, optional): Whether to ignore errors if the record is not found. Defaults to False.
            include_deleted (bool, optional): Whether to include soft-deleted records in the deletion. Defaults to False.
            commons (CommonsDependencies, optional): Common dependencies for the request. Defaults to None.

        Returns:
            bool: True if the record was successfully deleted, False otherwise.

        Raises:
            CoreErrorCode.NotFound: If the record is not found and `ignore_error` is False.

        """
        self.ensure_crud_provided()
        await self.get_by_id(_id=_id, ignore_error=ignore_error, include_deleted=include_deleted, commons=commons)
        result = await self.crud.delete_by_id(_id=_id)
        if not result:
            raise CoreErrorCode.NotFound(service_name=self.service_name, item=_id)
        return result

    async def soft_delete_by_id(self, _id: str, ignore_error: bool = False, commons: CommonsDependencies = None) -> dict:
        """
        Soft deletes a record by its ID.

        Args:
            _id (str): The ID of the record to soft delete.
            ignore_error (bool, optional): Whether to ignore errors if the record is not found. Defaults to False.
            commons (CommonsDependencies, optional): Common dependencies for the request. Defaults to None.

        Returns:
            dict: The updated record with the soft delete information.
        """
        self.ensure_crud_provided()
        data_update = {}
        data_update["deleted_at"] = self.get_current_datetime()
        data_update["deleted_by"] = self.get_current_user(commons=commons)
        result = await self.update_by_id(_id=_id, data=data_update, ignore_error=ignore_error, commons=commons)
        return result
