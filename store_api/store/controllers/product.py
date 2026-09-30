from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from store.core.exceptions import InsertionException, NotFoundException
from store.db.mongo import get_db
from store.schemas.product import ProductIn, ProductOut, ProductUpdate
from store.usecases.product import ProductUsecase

router = APIRouter(prefix="/products", tags=["products"])


def get_usecase(db=Depends(get_db)) -> ProductUsecase:
    return ProductUsecase(db)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=ProductOut)
async def create_product(
    body: ProductIn, usecase: ProductUsecase = Depends(get_usecase)
) -> ProductOut:
    try:
        return await usecase.create(body)
    except InsertionException as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=exc.message
        ) from exc


@router.get("", response_model=list[ProductOut])
async def list_products(
    price_gt: Decimal | None = Query(None, ge=0, description="Preço maior que"),
    price_lt: Decimal | None = Query(None, ge=0, description="Preço menor que"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    usecase: ProductUsecase = Depends(get_usecase),
) -> list[ProductOut]:
    if price_gt is not None and price_lt is not None and price_gt >= price_lt:
        raise HTTPException(
            status_code=422,
            detail="price_gt deve ser menor que price_lt",
        )
    return await usecase.query(price_gt, price_lt, limit, offset)


@router.get("/{id}", response_model=ProductOut)
async def get_product(
    id: UUID, usecase: ProductUsecase = Depends(get_usecase)
) -> ProductOut:
    try:
        return await usecase.get(id)
    except NotFoundException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc


@router.patch("/{id}", response_model=ProductOut)
async def update_product(
    id: UUID, body: ProductUpdate, usecase: ProductUsecase = Depends(get_usecase)
) -> ProductOut:
    try:
        return await usecase.update(id, body)
    except NotFoundException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    id: UUID, usecase: ProductUsecase = Depends(get_usecase)
) -> Response:
    try:
        await usecase.delete(id)
    except NotFoundException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)
