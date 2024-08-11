import math
import re

from bson import ObjectId

from .engine import Engine


class BaseCRUD:
    def __init__(self, database_engine: Engine, collection: str = None) -> None:
        self.database = database_engine
        if collection:
            self.collection = self.database[collection]
            self.collection_name = collection
            
    async def set_collection(self, collection: str):
        self.collection = self.database[collection]
        self.collection_name = collection
        
    async def count_documents(self, query: dict = None) -> int:
        return await self.collection.count_documents(filter=query)
    
    async def convert_object_id_to_string(self, document: dict):
        if document.get("_id") is None:
            return document
        document["_id"] = str(document["_id"])
        return document

    async def build_field_projection(self, fields_limit: list | str = None) -> dict:
        """
        Constructs a MongoDB field projection dictionary from a comma-separated string.
    
        Args:
            fields_limit (list | str): A list or string of field names to include in the projection.
                                For example, ["name", "age", "address"], "name,age,address".
    
        Returns:
            dict: A dictionary where keys are field names and values are 1, indicating the fields to include
                  in the MongoDB query results. If no fields are specified, an empty dictionary is returned.
        """
        if not fields_limit:
            return {}
        if isinstance(fields_limit, str):
            fields_limit = fields_limit.split(",")
        fields = {}
        for field in fields_limit:
            field = field.strip()
            fields[field] = 1
        return fields
    
    def convert_bools(self, value: dict | list | str) -> dict | list | str:
        """
        Converts string representations of booleans ("true" or "false") to actual boolean values (True, False) in a given data structure.

        Args:
            value (dict | list | str): The data structure containing the values to be converted.
                                       It can be a dictionary, list, or string.

        Returns:
            dict | list | str: The data structure with boolean string values converted to actual booleans.

        """
        bool_map = {"false": False, "true": True}
        if isinstance(value, dict):
            return {key: self.convert_bools(value=value) for key, value in value.items()}
        elif isinstance(value, list):
            return [self.convert_bools(value=item) for item in value]
        elif isinstance(value, str):
            return bool_map.get(value, value)
        return value

    def replace_special_chars(self, value: dict | str) -> dict | str:
        """
        Escapes special characters in strings within a given dictionary or string.
        
        
        This function finds special characters that have specific meanings in regular expressions 
        (e.g., *, +, ?, ^, $, {, }, (, ), |, [, ], \\) and escapes them by prefixing them with a backslash.
        This is useful when these characters need to be used in regular expression patterns or in other contexts 
        where they should be treated as literal characters.

        Args:
            value (dict | str): The input dictionary or string containing special characters.

        Returns:
            dict | str: The input dictionary with all string values having special characters escaped,
                        or a single string with special characters escaped using a backslash.
        """
        # Define the pattern for special characters
        pattern = r"([*+?^${}()|[\]\\])"
        # Replace the special characters with //
        if isinstance(value, dict):
            return {key: self.replace_special_chars(value=value) for key, value in value.items()}
        elif isinstance(value, str):
            return re.sub(pattern, r"\\\1", value)
        return value

    async def save(self, data: dict) -> str:
        """
        Inserts a single document into the collection.

        Args:
            data (dict): The document to be inserted into the collection.

        Returns:
            str: The ID of the inserted document as a string.
        """
        document = await self.collection.insert_one(document=data)
        return str(document.inserted_id)


    async def save_many(self, data: list) -> list | None:
        """
        Inserts multiple documents into the collection.
        
        Args:
            data (list): A list of documents to be inserted into the collection.
            
        Returns:
            bool: True if the insertion was successful, False otherwise.
        """
        documents = await self.collection.insert_many(documents=data)
        if not documents:
            return None
        results = []
        for document_id in documents.inserted_ids:
            results.append(str(document_id))
        return results

    async def save_unique(self, data: dict, unique_field: list | str) -> str | bool:
        """
        Saves a document into the collection if it does not already exist based on unique fields.
        
        Args:
            data (dict): The document to be inserted into the collection.
            unique_field (list | str): The field or list of fields that should be unique.
                                       If a document with the same values for these fields exists,
                                       the new document will not be inserted.
                                       
        Returns:
            str | bool: The ID of the inserted document as a string if insertion is successful,
                        False if a document with the same unique fields already exists.
        """
        is_exist = True
        
        if isinstance(unique_field, list):
            query = {}
            for key in data.keys():
                if key in unique_field:
                    query[key] = data[key]
            is_exist = await self.count_documents(query=query)
        elif isinstance(unique_field, str):
            is_exist = await self.collection.find_one(filter={unique_field: data[unique_field]})
        else:
            raise ValueError("The type of unique_field must be list or str")
        if is_exist:
            return False
        
        result = await self.save(data=data)
        return result
    
    async def aggregate_by_pipeline(self, pipeline: list) -> list:
        """
        Executes an aggregation pipeline on the collection.

        Args:
            pipeline (list): A list of aggregation stages to be applied.

        Returns:
            list: A list of documents resulting from the aggregation.
        """
        documents = self.collection.aggregate(pipeline=pipeline)
        results = []
        async for document in documents:
            results.append(document)
        return results

    async def update_by_id(self, _id: str, data: dict, query: dict = None) -> bool:
        """
        Updates a document in the collection based on its ID and an optional query.

        Args:
            _id (str): The ID of the document to be updated.
            data (dict): The data to update in the document.
            query (dict, optional): Additional query criteria for the update operation.

        Returns:
            bool: True if the document was successfully updated (i.e., at least one field was modified), 
                  False if no changes were made to the document or the document did not exist.
        """
        if not query:
            query = {}
        query.update({"_id": ObjectId(_id)})
        result = await self.collection.update_one(filter=query, update={"$set": data}, upsert=False)
        
        # The return statement `return update_result.modified_count > 0` checks if the number of documents 
        # modified by the update operation is greater than zero. If at least one document was modified, 
        # it returns True, indicating a successful update. If no documents were modified (either because 
        # the document did not exist or the data provided did not change any fields), it returns False.
        return result.modified_count > 0

    async def delete_by_id(self, _id: str, query: dict = None) -> bool:
        """
        Deletes a document from the collection based on its ID and an optional query.

        Args:
            _id (str): The ID of the document to be deleted.
            query (dict, optional): Additional query criteria for the delete operation.

        Returns:
            bool: True if the document was successfully deleted, False otherwise.
        """
        if not query:
            query = {}
        query.update({"_id": ObjectId(_id)})
        result = await self.collection.delete_one(filter=query)
        return result.deleted_count > 0
    
    async def delete_field_by_id(self, _id: str, field_name: str | list) -> bool:
        """
        Deletes specified fields from a document in the collection based on the document's ID.

        Args:
            _id (str): The ID of the document from which fields are to be deleted.
            field_name (str | list): The name of the field or a list of field names to be deleted.

        Returns:
            bool: True if the fields were successfully deleted, False otherwise.
        """
        if isinstance(field_name, str):
            field_name = [field_name]
        query = {"_id": ObjectId(_id)}
        data = {field: 1 for field in field_name}
        result = await self.collection.update_one(filter=query, update={"$unset": data})
        return result.modified_count > 0


    async def get_by_id(self, _id, fields_limit: list = None, query: dict = None) -> dict | None:
        """
        Retrieves a document from the collection based on its ID, with optional field limitations and additional query.

        Args:
            _id (str): The ID of the document to be retrieved.
            fields_limit (str, optional): A comma-separated string of field names to include in the result.
                                          If None, all fields are included.
            query (dict, optional): Additional query criteria to further refine the search.

        Returns:
            dict | None: The retrieved document with `_id` converted to a string, or None if no document is found.
        """
        fields_limit = await self.build_field_projection(fields_limit=fields_limit)
        if not query:
            query = {}
        query.update({"_id": ObjectId(_id)})
        query = self.replace_special_chars(value=query)
        result = await self.collection.find_one(filter=query, projection=fields_limit)
        if not result:
            return None
        result = await self.convert_object_id_to_string(document=result)
        return result

    async def get_by_field(self, data: str, field_name: str, fields_limit: list = None, query: dict = None) -> dict | None:
        """
        Retrieves a document from the collection based on a specific field value, with optional field limitations and additional query.

        Args:
            data (str): The value to search for in the specified field.
            field_name (str): The name of the field to search in.
            fields_limit (str, optional): A comma-separated string of field names to include in the result.
                                          If None, all fields are included.
            query (dict, optional): Additional query criteria to further refine the search.

        Returns:
            dict | None: The retrieved document with `_id` converted to a string, or None if no document is found.
        """
        fields_limit = await self.build_field_projection(fields_limit=fields_limit)
        if not query:
            query = {}
        query.update({field_name: data})
        query = self.replace_special_chars(value=query)
        result = await self.collection.find_one(filter=query, projection=fields_limit)
        if not result:
            return None
        result = await self.convert_object_id_to_string(document=result)
        return result

    async def get_all_by_field(self, data: str, field_name: str, fields_limit: list = None, query: dict = None) -> list | None:
        """
        Retrieves all documents from the collection that match a specific field value, with optional field limitations and additional query.

        Args:
            data (str): The value to search for in the specified field.
            field_name (str): The name of the field to search in.
            fields_limit (str, optional): A comma-separated string of field names to include in the results.
                                          If None, all fields are included.
            query (dict, optional): Additional query criteria to further refine the search.

        Returns:
            list | None: A list of dictionaries representing the retrieved documents with `_id` converted to a string,
                         or None if no documents are found.
        """
        fields_limit = await self.build_field_projection(fields_limit=fields_limit)
        if not query:
            query = {}
        query.update({field_name: data})
        query = self.replace_special_chars(value=query)
        documents = self.collection.find(filter=query, projection=fields_limit)
        if not documents:
            return None
        results = []
        async for document in documents:
            document = await self.convert_object_id_to_string(document=document)
            results.append(document)
        return results

    async def get_all(self, query: dict = None, search: str = None, search_in: list = None, page: int = None, limit: int = None, fields_limit: list = None, sort_by: str = None, order_by: str = None) -> dict:
        """
        Retrieves all documents from the collection based on various query, pagination, sorting, and field limitations.

        Args:
            query (dict, optional): The query criteria for querying the collection.
            search (str): A string to search for in the search_in fields.
            search_in (list, optional): A list of fields to search in if a search query is provided.
            page (int, optional): The page number for pagination.
            limit (int, optional): The number of documents per page.
            fields_limit (str, optional): A comma-separated string of field names to include in the results.
                                          If None, all fields are included.
            sort_by (str, optional): The field name to sort the results by.
            order_by (str, optional): The order to sort the results, either "asc" for ascending or "desc" for descending.

        Returns:
            dict | None: A dictionary containing the results, total number of items, total pages, and records per page.
        """
        # Converts a comma-separated string `fields_limit` into a dictionary where each field is a key with a value of 1.
        # If `fields_limit` is empty or None, an empty dictionary is returned.
        fields_limit = await self.build_field_projection(fields_limit=fields_limit)
        order_by = -1 if order_by == "desc" else 1
        sorting = [(sort_by, order_by)] if sort_by else None
        skip = (page - 1) * limit if page and limit else 0

        # Remove common pagination and sorting parameters from the query dictionary
        common_params = {"search", "page", "limit", "fields", "sort_by", "order_by"}
        query = {k: v for k, v in (query or {}).items() if k not in common_params}
        query = self.replace_special_chars(value=query)
        # Convert string representations of booleans to actual Boolean values in the query dictionary
        query = self.convert_bools(value=query)

        # Support search functionality within the query
        # If the 'search' key exists in the query dictionary, this block initializes or retrieves the '$or' list in the query,
        # then extends it with a series of dictionaries. Each dictionary represents a search condition on different fields,
        # specified in the 'search_in' list, using a regex pattern to perform a case-insensitive search of the 'search' string.
        # After constructing the search conditions, the 'search' key is removed from the query to prevent further processing issues.
        if search:
            search = self.replace_special_chars(value=search)
            query["$or"] = []
            query["$or"].extend({search_key: {"$regex": f".*{search}.*", "$options": "i"}} for search_key in search_in)

        documents = self.collection.find(filter=query, projection=fields_limit)
        if sorting:
            documents = documents.sort(sorting)
        if skip:
            documents = documents.skip(skip)
        if limit:
            documents = documents.limit(limit)

        result = {}
        result["records_per_page"] = 0
        results = []
        async for document in documents:
            document = await self.convert_object_id_to_string(document=document)
            results.append(document)
            result["records_per_page"] += 1
        total_records = await self.collection.count_documents(query)
        total_page = math.ceil(total_records / limit) if limit else 1
        result["total_items"] = total_records
        result["total_page"] = total_page
        result["results"] = results
        return result
