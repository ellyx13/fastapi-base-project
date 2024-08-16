from datetime import datetime

from db.base import BaseCRUD
from utils import value

from . import config
from .exceptions import ErrorCode as CoreErrorCode
from .schemas import CommonsDependencies


class BaseServices:
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
        maximum_document_limit (int): The maximum number of documents that can be retrieved, as defined in the configuration.

    """

    def __init__(self, service_name: str, crud: BaseCRUD = None) -> None:
        self.crud = crud
        self.service_name = service_name
        self.maximum_document_limit = config.MAXIMUM_DOCUMENT_LIMIT
        self.ownership_field = config.OWNERSHIP_FIELD

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
        return commons.current_user

    def get_current_user_type(self, commons: CommonsDependencies):
        """
        Retrieves the type of the current user from the provided common dependencies.

        Args:
            commons (CommonsDependencies): The common dependencies containing the user type information.

        Returns:
            str: The type of the current user (e.g., admin, customer).

        """
        return commons.user_type

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
        query[self.ownership_field] = current_user_id
        return query

    async def get_by_id(self, _id, fields_limit: list | str = None, ignore_error: bool = False, include_deleted: bool = False, commons: CommonsDependencies = None) -> dict:
        """
        Retrieves a record by its ID.

        Args:
            _id (str): The ID of the record to retrieve.
            fields_limit (list | str, optional): Fields to include in the response. Defaults to None.
            ignore_error (bool, optional): Whether to ignore errors if the record is not found. Defaults to False.
            include_deleted (bool, optional): Whether to include soft-deleted records. Defaults to False.
            commons (CommonsDependencies, optional): Common dependencies for the request. Defaults to None.

        Returns:
            dict: A dictionary representing the retrieved record.

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
        return item

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
            dict: A dictionary containing the retrieved records and additional metadata.

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

        item = await self.crud.get_all(query=query, search=search, search_in=search_in, page=page, limit=limit, fields_limit=fields_limit, sort_by=sort_by, order_by=order_by)
        return item

    async def get_by_field(
        self, data: str, field_name: str, fields_limit: list | str = None, ignore_error: bool = False, include_deleted: bool = False, commons: CommonsDependencies = None
    ) -> dict:
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
            dict: A dictionary representing the retrieved record.

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

        item = await self.crud.get_by_field(data=data, field_name=field_name, fields_limit=fields_limit, query=query)
        if not item and not ignore_error:
            raise CoreErrorCode.NotFound(service_name=self.service_name, item=data)
        return item

    async def _check_modified(self, old_data: dict, new_data: dict, ignore_error: bool) -> bool:
        """
        Checks if any data has been modified in the update request.

        Args:
            old_data (dict): The original data before modification.
            new_data (dict): The new data to compare against the original data.
            ignore_error (bool): Whether to ignore errors if no modifications are found.

        Returns:
            bool: True if data has been modified, False otherwise.

        Raises:
            CoreErrorCode.NotModified: If no modifications are detected and `ignore_error` is False.

        """
        for key, item_value in new_data.items():
            if key in ["updated_at", "updated_by"]:
                continue
            if old_data.get(key) != item_value:
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

    async def save(self, data: dict) -> dict:
        """
        Saves a new record to the database.

        Args:
            data (dict): The data to be saved.

        Returns:
            dict: The saved record, retrieved by its ID.
        """
        self.ensure_crud_provided()
        item = await self.crud.save(data=data)
        result = await self.get_by_id(_id=item)
        return result

    async def save_many(self, data: list) -> list[dict]:
        """
        Saves multiple records to the database.

        Args:
            data (list): A list of dictionaries, each representing a record to be saved.

        Returns:
            list[dict]: A list of saved records, each retrieved by its ID.

        """
        self.ensure_crud_provided()
        items = await self.crud.save_many(data=data)
        results = []
        for item_id in items:
            item = await self.get_by_id(_id=item_id)
            results.append(item)
        return results

    async def save_unique(self, data: dict, unique_field: str | list, ignore_error: bool = False) -> dict:
        """
        Saves a new record to the database, ensuring that specified fields are unique.

        Args:
            data (dict): The data to be saved.
            unique_field (str | list): The field or fields that must be unique in the database.
            ignore_error (bool, optional): Whether to ignore errors if a conflict is found. Defaults to False.

        Returns:
            dict: The saved record, retrieved by its ID.

        Raises:
            CoreErrorCode.Conflict: If a conflict is detected and `ignore_error` is False.

        """
        self.ensure_crud_provided()
        item = await self.crud.save_unique(data=data, unique_field=unique_field)
        if not item and not ignore_error:
            if isinstance(unique_field, list):
                unique_value = data[unique_field[0]]
            else:
                unique_value = data[unique_field]
            raise CoreErrorCode.Conflict(service_name=self.service_name, item=unique_value)
        result = await self.get_by_id(_id=item)
        return result

    async def update_by_id(
        self, _id: str, data: dict, unique_field: str | list = None, check_modified: bool = True, ignore_error: bool = False, include_deleted: bool = False, commons: CommonsDependencies = None
    ) -> dict | None:
        """
        Updates a record by its ID.

        Args:
            _id (str): The ID of the record to update.
            data (dict): The new data to update the record with.
            unique_field (str | list, optional): The field or fields that must be unique in the database. Defaults to None.
            check_modified (bool, optional): Whether to check if the data has been modified before updating. Defaults to True.
            ignore_error (bool, optional): Whether to ignore errors if the record is not found or not modified. Defaults to False.
            include_deleted (bool, optional): Whether to include soft-deleted records in the update. Defaults to False.
            commons (CommonsDependencies, optional): Common dependencies for the request. Defaults to None.

        Returns:
            dict | None: The updated record, or None if `ignore_error` is True and the record is not found.

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
        await self.crud.update_by_id(_id=_id, data=data)
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
