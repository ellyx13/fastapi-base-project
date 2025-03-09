from unittest.mock import AsyncMock, patch

import pytest
from auth.services import auth_services
from bcrypt import gensalt, hashpw
from exceptions import CustomException
from users.exceptions import UserErrorCode
from users.models import Users
from users.services import UserServices

service_name = "users"


@pytest.fixture
def user_services():
    return UserServices(service_name=service_name, crud=AsyncMock(), model=Users)


@pytest.mark.asyncio
async def test_register_success(user_services):
    mock_user_data = {"email": "test@example.com", "password": "password123", "fullname": "Test User"}

    with patch.object(user_services, "save_unique", AsyncMock(return_value={"_id": "user_id", "type": "user"})), patch.object(
        user_services, "update_by_id", AsyncMock(return_value={"_id": "user_id", "type": "user"})
    ), patch.object(auth_services, "create_access_token", AsyncMock(return_value="fake_token")):
        result = await user_services.register(fullname=mock_user_data["fullname"], email=mock_user_data["email"], password=mock_user_data["password"])

        assert result["_id"] == "user_id"


@pytest.mark.asyncio
async def test_register_duplicate_email(user_services):
    mock_user_data = {"email": "duplicate@example.com", "password": "password123", "fullname": "Test User"}

    with patch.object(user_services, "save_unique", AsyncMock(side_effect=UserErrorCode.Conflict(service_name="users", item="email"))):
        with pytest.raises(CustomException) as exc:
            await user_services.register(fullname=mock_user_data["fullname"], email=mock_user_data["email"], password=mock_user_data["password"])

        assert exc.value.type == "users/warning/conflict"
        assert exc.value.status == 409
        assert exc.value.title == "Conflict."


@pytest.mark.asyncio
async def test_login_success(user_services):
    mock_login_data = {"email": "test@example.com", "password": "password123"}
    mock_user = [{"_id": "user_id", "email": "test@example.com", "type": "user", "password": hashpw(mock_login_data["password"].encode("utf-8"), gensalt())}]

    with patch.object(user_services, "get_by_field", AsyncMock(return_value=mock_user)), patch.object(auth_services, "create_access_token", AsyncMock(return_value="fake_token")):
        result = await user_services.login(email=mock_login_data["email"], password=mock_login_data["password"])

        assert result["_id"] == "user_id"


@pytest.mark.asyncio
async def test_login_invalid_password(user_services):
    mock_login_data = {"email": "test@example.com", "password": "wrongpassword"}
    mock_user = [{"_id": "user_id", "email": "test@example.com", "type": "user", "password": hashpw(mock_login_data["password"].encode("utf-8"), gensalt())}]

    with patch.object(user_services, "get_by_field", AsyncMock(return_value=mock_user)), patch.object(auth_services, "validate_hash", AsyncMock(side_effect=UserErrorCode.Unauthorize())):
        with pytest.raises(CustomException) as exc:
            await user_services.login(email=mock_login_data["email"], password=mock_login_data["password"])

        assert exc.value.type == "core/warning/unauthorize"
        assert exc.value.status == 401
        assert exc.value.title == "Unauthorize."


@pytest.mark.asyncio
async def test_edit_user_success(user_services):
    mock_edit_data = {"fullname": "Updated Name"}
    mock_user = {"_id": "user_id", "fullname": "Test User"}
    commons = AsyncMock()

    with patch.object(user_services, "get_by_id", AsyncMock(return_value=mock_user)), patch.object(user_services, "update_by_id", AsyncMock(return_value={"_id": "user_id", **mock_edit_data})):
        result = await user_services.edit(_id="user_id", data=mock_edit_data, commons=commons)

        assert result["fullname"] == "Updated Name"


@pytest.mark.asyncio
async def test_edit_user_not_found(user_services):
    mock_edit_data = {"fullname": "Updated Name"}
    commons = AsyncMock()

    with patch.object(user_services, "get_by_id", AsyncMock(side_effect=UserErrorCode.NotFound(service_name=service_name, item="user_id"))):
        with pytest.raises(CustomException) as exc:
            await user_services.edit(_id="user_id", data=mock_edit_data, commons=commons)

        assert exc.value.type == "users/warning/not-found"
        assert exc.value.status == 404
        assert exc.value.title == "Not found."
