import asyncio
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from store.core.exceptions import InsertionException, NotFoundException
from store.schemas.product import ProductIn, ProductOut, ProductUpdate
from tests.factories import product_data, products_with_prices


async def test_create_success(usecase):
    result = await usecase.create(ProductIn(**product_data()))

    assert isinstance(result, ProductOut)
    assert result.name == "iPhone 14 Pro Max"


async def test_create_insertion_error_raises_insertion_exception(usecase):
    usecase.collection = AsyncMock()
    usecase.collection.insert_one.side_effect = RuntimeError("db fora do ar")

    with pytest.raises(InsertionException) as err:
        await usecase.create(ProductIn(**product_data()))

    assert "cadastrar o produto" in err.value.message


async def test_get_success(usecase):
    created = await usecase.create(ProductIn(**product_data()))

    result = await usecase.get(created.id)

    assert result.id == created.id
    assert result.price == Decimal("8500.00")


async def test_get_not_found(usecase):
    missing = uuid4()

    with pytest.raises(NotFoundException) as err:
        await usecase.get(missing)

    assert err.value.message == f"Produto não encontrado com o id: {missing}"


async def test_query_returns_all(usecase):
    for data in products_with_prices():
        await usecase.create(ProductIn(**data))

    assert len(await usecase.query()) == 6


async def test_query_price_filter_is_exclusive(usecase):
    for data in products_with_prices():
        await usecase.create(ProductIn(**data))

    result = await usecase.query(price_gt=Decimal("5000"), price_lt=Decimal("8000"))

    # 5000 e 8000 ficam de fora (price > 5000 and price < 8000)
    assert sorted(p.price for p in result) == [Decimal("6500"), Decimal("7500")]


async def test_query_only_price_gt(usecase):
    for data in products_with_prices():
        await usecase.create(ProductIn(**data))

    result = await usecase.query(price_gt=Decimal("8000"))

    assert [p.price for p in result] == [Decimal("9500")]


async def test_query_pagination(usecase):
    for data in products_with_prices():
        await usecase.create(ProductIn(**data))

    assert len(await usecase.query(limit=2)) == 2
    assert len(await usecase.query(limit=10, offset=4)) == 2


async def test_update_success_refreshes_updated_at(usecase):
    created = await usecase.create(ProductIn(**product_data()))
    await asyncio.sleep(0.01)

    result = await usecase.update(created.id, ProductUpdate(quantity=99, price=Decimal("7000")))

    assert result.quantity == 99
    assert result.price == Decimal("7000")
    assert result.name == created.name
    assert result.updated_at > created.updated_at


async def test_update_allows_custom_updated_at(usecase):
    created = await usecase.create(ProductIn(**product_data()))
    custom = datetime(2030, 1, 1, tzinfo=timezone.utc)

    result = await usecase.update(created.id, ProductUpdate(updated_at=custom))

    assert result.updated_at == custom


async def test_update_not_found(usecase):
    with pytest.raises(NotFoundException):
        await usecase.update(uuid4(), ProductUpdate(quantity=1))


async def test_delete_success(usecase):
    created = await usecase.create(ProductIn(**product_data()))

    await usecase.delete(created.id)

    with pytest.raises(NotFoundException):
        await usecase.get(created.id)


async def test_delete_not_found(usecase):
    with pytest.raises(NotFoundException):
        await usecase.delete(uuid4())
