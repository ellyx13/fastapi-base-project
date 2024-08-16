import pytest
from bson import ObjectId
from db.base import BaseCRUD
from db.engine import app_engine

collection_name = "test"
base_crud = BaseCRUD(database_engine=app_engine, collection=collection_name)


# ------------- Testing the Constructor and set_collection method ------------ #
@pytest.mark.anyio(scope="session")
def test_constructor():
    assert base_crud.collection_name == collection_name


@pytest.mark.asyncio(scope="session")
async def test_set_collection():
    await base_crud.set_collection(collection="new_collection")
    assert base_crud.collection_name == "new_collection"


# ---------------------------- Testing save method --------------------------- #
@pytest.mark.asyncio(scope="session")
async def test_save_one():
    data = {"name": "John Doe", "age": 30}
    item = await base_crud.save(data=data)
    assert isinstance(item, str)


@pytest.mark.asyncio(scope="session")
async def test_save_many():
    data = [{"name": "Alice", "age": 25}, {"name": "John Doe", "age": 28}]
    items = await base_crud.save_many(data=data)
    assert isinstance(items, list)
    for item_id in items:
        item = await base_crud.get_by_id(_id=item_id)
        assert item is not None


@pytest.mark.asyncio(scope="session")
async def test_save_unique():
    data = {"name": "Unique", "age": 30}
    item = await base_crud.save_unique(data=data, unique_field="name")
    assert isinstance(item, str)

    item = await base_crud.save_unique(data=data, unique_field="name")
    assert item is False


# ---------------------- Testing count_documents method ---------------------- #
@pytest.mark.asyncio(scope="session")
async def test_count_documents():
    count = await base_crud.count_documents(query={"name": "John Doe"})
    assert count == 2

    count = await base_crud.count_documents(query={"name": "Not Found"})
    assert count == 0


# ------------------------ Testing Document Conversion ----------------------- #
@pytest.mark.asyncio(scope="session")
async def test_convert_object_id_to_string():
    document = {"_id": ObjectId()}
    result = await base_crud.convert_object_id_to_string(document=document)
    assert isinstance(result["_id"], str)


# ------------------------- Testing Field Projection ------------------------- #
@pytest.mark.asyncio(scope="session")
async def test_build_field_projection():
    projection = await base_crud.build_field_projection(fields_limit=["name", "age"])
    assert projection == {"name": 1, "age": 1}


# -------------------------- Testing Get Operations -------------------------- #
@pytest.mark.asyncio(scope="session")
async def test_get_by_id():
    data = {"name": "John Doe 1", "age": 30}
    item_id = await base_crud.save(data=data)

    item = await base_crud.get_by_id(_id=item_id)
    assert item is not None
    assert item["name"] == "John Doe 1"


@pytest.mark.asyncio(scope="session")
async def test_get_by_field():
    item = await base_crud.get_by_field(data="John Doe", field_name="name")
    assert item is not None
    assert item["name"] == "John Doe"


@pytest.mark.asyncio(scope="session")
async def test_get_all_by_field():
    items = await base_crud.get_all_by_field(data="John Doe", field_name="name")
    assert isinstance(items, list)
    assert len(items) == 2


@pytest.mark.asyncio(scope="session")
async def test_get_all():
    items = await base_crud.get_all(query={"name": "John Doe"})
    assert items["total_items"] == 2

    items = await base_crud.get_all(query={"name": "John Doe"}, limit=1)
    assert items["records_per_page"] == 1

    items = await base_crud.get_all(query={"name": "Not Found 1"})
    assert items["total_items"] == 0

    items = await base_crud.get_all(search="John Doe", search_in=["name"])
    assert items["total_items"] == 3


# ------------------------- Testing Update Operations ------------------------ #
@pytest.mark.asyncio(scope="session")
async def test_update_by_id():
    item = await base_crud.get_by_field(data="John Doe", field_name="name")

    success = await base_crud.update_by_id(item["_id"], data={"name": "New Name"})
    assert success is True

    item = await base_crud.get_by_id(_id=item["_id"])
    assert item["name"] == "New Name"


# ------------------------- Testing Delete Operations ------------------------ #
@pytest.mark.asyncio(scope="session")
async def test_delete_by_id():
    item = await base_crud.get_by_field(data="John Doe", field_name="name")

    success = await base_crud.delete_by_id(_id=item["_id"])
    assert success is True

    item = await base_crud.get_by_id(_id=item["_id"])
    assert item is None
