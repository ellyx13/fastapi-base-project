import pytest
from httpx import ASGITransport, AsyncClient
from main import app

from tests.config import settings


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url=settings.base_url) as client:
        print("Client is ready")
        yield client
