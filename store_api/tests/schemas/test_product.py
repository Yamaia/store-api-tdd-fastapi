from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

import pytest
from pydantic import ValidationError

from store.schemas.product import ProductIn, ProductOut, ProductUpdate
from tests.factories import product_data


def test_product_in_success():
    product = ProductIn(**product_data())

    assert product.name == "iPhone 14 Pro Max"
    assert product.price == Decimal("8500.00")


def test_product_in_missing_field():
    data = product_data()
    data.pop("name")

    with pytest.raises(ValidationError) as err:
        ProductIn(**data)

    assert err.value.errors()[0]["loc"] == ("name",)
    assert err.value.errors()[0]["type"] == "missing"


@pytest.mark.parametrize(
    "field,value",
    [
        ("name", ""),
        ("quantity", -1),
        ("price", "-1"),
        ("price", "abc"),
        ("status", "talvez"),
    ],
)
def test_product_in_invalid_values(field, value):
    with pytest.raises(ValidationError):
        ProductIn(**product_data(**{field: value}))


def test_product_out_generates_defaults():
    product = ProductOut(**product_data())

    assert isinstance(product.id, UUID)
    assert isinstance(product.created_at, datetime)
    assert isinstance(product.updated_at, datetime)


def test_product_update_all_fields_optional():
    assert ProductUpdate().model_dump(exclude_none=True) == {}


def test_product_update_accepts_updated_at():
    new_date = datetime(2030, 1, 1, tzinfo=timezone.utc)

    assert ProductUpdate(updated_at=new_date).updated_at == new_date
