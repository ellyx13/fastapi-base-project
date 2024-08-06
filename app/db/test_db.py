import pytest
import time
from base import BaseCRUD
from engine import app_engine


test_crud = BaseCRUD(database_engine=app_engine, collection="test")

@pytest.mark.anyio
async def test_save():
    data = {"name": "John Doe", "age": 30}
    item = await test_crud.save(data=data)
    assert item["name"] == "John Doe" and item["age"] == 30
    

@pytest.mark.anyio
async def test_save_many():
    data = [
        {"name": "Alice", "age": 25},
        {"name": "Bob", "age": 28}
    ]
    items = await test_crud.save_many(data=data)
    assert items is True