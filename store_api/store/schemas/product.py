from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ProductBase(BaseModel):
    name: str = Field(min_length=1, description="Nome do produto")
    quantity: int = Field(ge=0, description="Quantidade em estoque")
    price: Decimal = Field(ge=0, max_digits=12, decimal_places=2, description="Preço")
    status: bool = Field(description="Produto ativo?")


class ProductIn(ProductBase):
    """Corpo da requisição de criação."""


class ProductOut(ProductBase):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1)
    quantity: int | None = Field(default=None, ge=0)
    price: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    status: bool | None = None
    updated_at: datetime | None = Field(
        default=None, description="Opcional. Se omitido, usa o horário atual."
    )
