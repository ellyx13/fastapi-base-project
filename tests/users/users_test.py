import pytest
from httpx import AsyncClient

payload_user_register = {"fullname": "testuser", "email": "test@example.com", "password": "testpassword"}


@pytest.mark.asyncio(scope="session")
async def test_user_register_success(client: AsyncClient):
    response = await client.post("v1/users/register", json=payload_user_register)
    assert response.status_code == 201


@pytest.mark.asyncio(scope="session")
async def test_user_login(client: AsyncClient):
    payload = {"email": "test@example.com", "password": "testpassword"}
    response = await client.post("v1/users/login", json=payload)
    assert response.status_code == 201
    response = response.json()
    assert "access_token" in response
    return response


@pytest.mark.asyncio(scope="session")
async def test_get_me(client: AsyncClient):
    user = await test_user_login(client)
    headers = {"Authorization": f"Bearer {user['access_token']}"}
    response = await client.get("v1/users/me", headers=headers)
    assert response.status_code == 200


@pytest.mark.asyncio(scope="session")
async def test_user_detail(client: AsyncClient):
    user = await test_user_login(client)
    user_id = user["_id"]
    headers = {"Authorization": f"Bearer {user['access_token']}"}
    response = await client.get(f"v1/users/{user_id}", headers=headers)
    assert response.status_code == 200


@pytest.mark.asyncio(scope="session")
async def test_user_edit(client: AsyncClient):
    user = await test_user_login(client)
    user_id = user["_id"]
    headers = {"Authorization": f"Bearer {user['access_token']}"}
    payload = {"fullname": "new_name"}
    response = await client.put(f"v1/users/{user_id}", headers=headers, json=payload)
    assert response.status_code == 200
    assert response.json()["fullname"] == "new_name"
