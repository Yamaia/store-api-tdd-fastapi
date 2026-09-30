from datetime import datetime, timezone
from decimal import Decimal
from typing import Any
from uuid import UUID

from pymongo import ReturnDocument

from store.core.exceptions import InsertionException, NotFoundException
from store.schemas.product import ProductIn, ProductOut, ProductUpdate


def _to_cents(price: Decimal) -> int:
    return int((price * 100).to_integral_value())


def _encode(data: dict[str, Any]) -> dict[str, Any]:
    """Converte tipos Python para tipos aceitos pelo MongoDB.

    O preço é guardado em centavos (inteiro): exato, sem erro de ponto flutuante
    e comparável nos filtros do banco.
    """
    encoded = dict(data)
    if "id" in encoded:
        encoded["id"] = str(encoded["id"])
    if "price" in encoded:
        encoded["price_cents"] = _to_cents(encoded.pop("price"))
    return encoded


def _decode(doc: dict[str, Any]) -> ProductOut:
    doc = dict(doc)
    doc["price"] = Decimal(doc.pop("price_cents")).scaleb(-2)
    return ProductOut(**doc)


class ProductUsecase:
    def __init__(self, db) -> None:
        self.collection = db["products"]

    @staticmethod
    def _not_found(id: UUID) -> NotFoundException:
        return NotFoundException(f"Produto não encontrado com o id: {id}")

    async def create(self, body: ProductIn) -> ProductOut:
        product = ProductOut(**body.model_dump())
        try:
            await self.collection.insert_one(_encode(product.model_dump()))
        except Exception as exc:
            raise InsertionException(
                "Não foi possível cadastrar o produto. Tente novamente mais tarde."
            ) from exc
        return product

    async def get(self, id: UUID) -> ProductOut:
        doc = await self.collection.find_one({"id": str(id)}, {"_id": 0})
        if doc is None:
            raise self._not_found(id)
        return _decode(doc)

    async def query(
        self,
        price_gt: Decimal | None = None,
        price_lt: Decimal | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[ProductOut]:
        price_filter: dict[str, int] = {}
        if price_gt is not None:
            price_filter["$gt"] = _to_cents(price_gt)
        if price_lt is not None:
            price_filter["$lt"] = _to_cents(price_lt)
        filters = {"price_cents": price_filter} if price_filter else {}

        cursor = (
            self.collection.find(filters, {"_id": 0})
            .sort("created_at", 1)
            .skip(offset)
            .limit(limit)
        )
        docs = await cursor.to_list(length=limit)
        return [_decode(doc) for doc in docs]

    async def update(self, id: UUID, body: ProductUpdate) -> ProductOut:
        data = body.model_dump(exclude_none=True)
        # updated_at = agora, a menos que o cliente envie um valor.
        data.setdefault("updated_at", datetime.now(timezone.utc))

        doc = await self.collection.find_one_and_update(
            {"id": str(id)},
            {"$set": _encode(data)},
            projection={"_id": 0},
            return_document=ReturnDocument.AFTER,
        )
        if doc is None:
            raise self._not_found(id)
        return _decode(doc)

    async def delete(self, id: UUID) -> None:
        result = await self.collection.delete_one({"id": str(id)})
        if result.deleted_count == 0:
            raise self._not_found(id)
