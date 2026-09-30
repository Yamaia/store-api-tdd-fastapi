from decimal import Decimal
from uuid import uuid4

from store.core.exceptions import InsertionException
from store.usecases.product import ProductUsecase
from tests.factories import product_data, products_with_prices


async def _create(client, **overrides) -> dict:
    response = await client.post("/products", json=product_data(**overrides))
    assert response.status_code == 201
    return response.json()


async def test_post_success(client):
    response = await client.post("/products", json=product_data())

    body = response.json()
    assert response.status_code == 201
    assert body["name"] == "iPhone 14 Pro Max"
    assert Decimal(body["price"]) == Decimal("8500")
    assert {"id", "created_at", "updated_at"} <= body.keys()


async def test_post_invalid_body_returns_422(client):
    response = await client.post("/products", json={"name": "sem preço"})

    assert response.status_code == 422


async def test_post_insertion_error_returns_500_with_friendly_message(client, monkeypatch):
    async def boom(self, body):
        raise InsertionException("Não foi possível cadastrar o produto. Tente novamente mais tarde.")

    monkeypatch.setattr(ProductUsecase, "create", boom)

    response = await client.post("/products", json=product_data())

    assert response.status_code == 500
    assert response.json() == {
        "detail": "Não foi possível cadastrar o produto. Tente novamente mais tarde."
    }


async def test_get_by_id_success(client):
    created = await _create(client)

    response = await client.get(f"/products/{created['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


async def test_get_by_id_not_found(client):
    missing = uuid4()

    response = await client.get(f"/products/{missing}")

    assert response.status_code == 404
    assert response.json() == {"detail": f"Produto não encontrado com o id: {missing}"}


async def test_list_products(client):
    for data in products_with_prices():
        await client.post("/products", json=data)

    response = await client.get("/products")

    assert response.status_code == 200
    assert len(response.json()) == 6


async def test_list_products_price_filter(client):
    for data in products_with_prices():
        await client.post("/products", json=data)

    response = await client.get("/products", params={"price_gt": 5000, "price_lt": 8000})

    prices = sorted(Decimal(p["price"]) for p in response.json())
    assert response.status_code == 200
    assert prices == [Decimal("6500"), Decimal("7500")]


async def test_list_products_invalid_price_range_returns_422(client):
    response = await client.get("/products", params={"price_gt": 8000, "price_lt": 5000})

    assert response.status_code == 422
    assert response.json()["detail"] == "price_gt deve ser menor que price_lt"


async def test_patch_success_updates_updated_at(client):
    created = await _create(client)

    response = await client.patch(f"/products/{created['id']}", json={"quantity": 5})

    body = response.json()
    assert response.status_code == 200
    assert body["quantity"] == 5
    assert body["name"] == created["name"]
    assert body["updated_at"] > created["updated_at"]


async def test_patch_allows_custom_updated_at(client):
    created = await _create(client)

    response = await client.patch(
        f"/products/{created['id']}", json={"updated_at": "2030-01-01T00:00:00Z"}
    )

    assert response.status_code == 200
    assert response.json()["updated_at"].startswith("2030-01-01T00:00:00")


async def test_patch_not_found_returns_friendly_message(client):
    missing = uuid4()

    response = await client.patch(f"/products/{missing}", json={"quantity": 5})

    assert response.status_code == 404
    assert response.json() == {"detail": f"Produto não encontrado com o id: {missing}"}


async def test_delete_success(client):
    created = await _create(client)

    response = await client.delete(f"/products/{created['id']}")

    assert response.status_code == 204
    assert (await client.get(f"/products/{created['id']}")).status_code == 404


async def test_delete_not_found(client):
    response = await client.delete(f"/products/{uuid4()}")

    assert response.status_code == 404
