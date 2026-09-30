import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from mongomock_motor import AsyncMongoMockClient

from store.db.mongo import get_db
from store.main import app
from store.usecases.product import ProductUsecase


@pytest.fixture
def db():
    return AsyncMongoMockClient(tz_aware=True)["store_test"]


@pytest.fixture
def usecase(db):
    return ProductUsecase(db)


@pytest_asyncio.fixture
async def client(db):
    app.dependency_overrides[get_db] = lambda: db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()
