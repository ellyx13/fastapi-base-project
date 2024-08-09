from .services import BaseServices

NOT_DECLARED_SERVICE = "Service must be an instance of BaseServices. Maybe the service has not been declared when creating the class Controllers"


class BaseControllers:
    def __init__(self, controller_name: str, service: BaseServices = None) -> None:
        self.controller_name = controller_name
        self.service = service
        self.max_record_limit = self.service.maximum_document_limit

    async def get_all(
        self,
        query: dict = None,
        search: str = None,
        search_in: list = None,                            
        page: int = 1,
        limit: int = 20,
        fields_limit: list = None,
        sort_by: str = "created_at",
        order_by: str = "desc",
        include_deleted: bool = False,                                                                                                                                                              
    ) -> dict:
        if not isinstance(self.service, BaseServices):
            raise TypeError(NOT_DECLARED_SERVICE)
        results = await self.service.get_all(
            query=query, 
            search=search, 
            search_in=search_in, 
            page=page, limit=limit, 
            fields_limit=fields_limit, 
            sort_by=sort_by, 
            order_by=order_by, 
            include_deleted=include_deleted
        )
        return results

    async def get_by_id(self, _id, fields_limit: list = None, query: dict = None, ignore_error: bool = False, include_deleted: bool = False) -> dict:
        if not isinstance(self.service, BaseServices):
            raise TypeError(NOT_DECLARED_SERVICE)
        result = await self.service.get_by_id(_id=_id, fields_limit=fields_limit, query=query, ignore_error=ignore_error, include_deleted=include_deleted)
        return result

    async def get_by_field(self, data: str, field_name: str, fields_limit: list = None, ignore_error: bool = False, include_deleted: bool = False) -> dict:
        if not isinstance(self.service, BaseServices):
            raise TypeError(NOT_DECLARED_SERVICE)
        result = await self.service.get_by_field(data=data, field_name=field_name, fields_limit=fields_limit, ignore_error=ignore_error, include_deleted=include_deleted)
        return result

    async def soft_delete_by_id(self, _id: str) -> dict:
        if not isinstance(self.service, BaseServices):
            raise TypeError(NOT_DECLARED_SERVICE)
        result = await self.service.soft_delete_by_id(_id=_id)
        return result
