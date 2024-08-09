from db.base import BaseCRUD
from . import config
from datetime import datetime
from .exceptions import ErrorCode as CoreErrorCode
from .schemas import PaginationParams

class BaseServices:
    def __init__(self, crud: BaseCRUD, service_name: str) -> None:
        self.crud = crud
        self.service_name = service_name
        self.maximum_document_limit = config.MAXIMUM_DOCUMENT_LIMIT

    def get_current_datetime(self) -> datetime:
        """
            Returns:
                datetime: ISO 8601 Date Format: YYYY-MM-DD HH:MM:SS.sssZ
        """
        return datetime.now()

    async def get_by_id(self, _id, fields_limit: list = None, query: dict = None, ignore_error: bool = False, include_deleted: bool = False) -> dict:
        if not include_deleted:
            if not query:
                query = {}
            query.update({"deleted_at": None})
        item = await self.crud.get_by_id(_id=_id, fields_limit=fields_limit, query=query)
        if not item and not ignore_error:
            raise CoreErrorCode.NotFound(service_name=self.service_name, item=_id)
        return item

    async def get_all(self, query: dict = None, search: str = None, search_in: list = None, page: int = 1, limit: int = 20, fields_limit: list = None, sort_by: str = 'created_at', order_by: str = 'desc', include_deleted: bool = False) -> dict:
        if not include_deleted:
            if not query:
                query = {}
            query.update({"deleted_at": None})
        item = await self.crud.get_all(query=query, search=search, search_in=search_in, page=page, limit=limit, fields_limit=fields_limit, sort_by=sort_by, order_by=order_by)
        return item

    async def get_by_field(self, data: str, field_name: str, fields_limit: list = None, ignore_error: bool = False, include_deleted: bool = False) -> dict:
        query = {}
        if not include_deleted:
            query.update({"deleted_at": None})
        item = await self.crud.get_by_field(data=data, field_name=field_name, fields_limit=fields_limit, query=query)
        if not item and not ignore_error:
            raise CoreErrorCode.NotFound(service_name=self.service_name, item=data)
        return item

    async def _check_modified(self, old_data: dict, new_data: dict, ignore_error: bool) -> bool:
        for key, value in new_data.items():
            if key in ["updated_at", "updated_by"]:
                continue
            if old_data.get(key) != value:
                return True
        if ignore_error:
            return False
        raise CoreErrorCode.NotModified(service_name=self.service_name)

    async def _check_unique(self, data: dict, unique_field: str | list, ignore_error: bool = False) -> bool:
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
        item = await self.crud.save(data=data)
        result = await self.get_by_id(_id=item)
        return result
    
    async def save_many(self, data: list) -> list[dict]:
        items = await self.crud.save_many(data=data)
        results = []
        for item_id in items:
            item = await self.get_by_id(_id=item_id)
            results.append(item)
        return results

    async def save_unique(self, data: dict, unique_field: str | list, ignore_error: bool = False) -> dict:
        item = await self.crud.save_unique(data=data, unique_field=unique_field)
        if not item and not ignore_error:
            if isinstance(unique_field, list):
                unique_value = data[unique_field[0]]
            else:
                unique_value = data[unique_field]
            raise CoreErrorCode.Conflict(service_name=self.service_name, item=unique_value)
        result = await self.get_by_id(_id=item)
        return result
    
    async def update_by_id(self, _id: str, data: dict, unique_field: str | list = None, check_modified: bool = True, ignore_error: bool = False, include_deleted: bool = False) -> dict | None:
        item = await self.get_by_id(_id=_id, ignore_error=ignore_error, include_deleted=include_deleted)
        if not item and ignore_error:
            return None
        if check_modified:
            await self._check_modified(old_data=item, new_data=data, ignore_error=ignore_error)
        if unique_field:
            await self._check_unique(data=data, unique_field=unique_field, ignore_error=ignore_error)
        await self.crud.update_by_id(_id=_id, data=data)
        result = await self.get_by_id(_id=_id, ignore_error=ignore_error, include_deleted=include_deleted)
        return result
        
    async def hard_delete_by_id(self, _id: str, query: dict = None) -> bool:
        result = await self.crud.delete_by_id(_id=_id, query=query)
        if not result:
            raise CoreErrorCode.NotFound(service_name=self.service_name, item=_id)
        return result

    async def soft_delete_by_id(self, _id: str) -> dict:
        data_update = {}
        data_update["deleted_at"] = self.get_current_datetime()
        result = await self.update_by_id(_id=_id, data=data_update)
        return result



