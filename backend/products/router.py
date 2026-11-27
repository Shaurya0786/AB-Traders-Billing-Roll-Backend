from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.exc import IntegrityError

from ..database import session
from ..schemas import ProductCreate, ProductUpdate
from ..security import require_admin
from .service import ProductService

router = APIRouter(prefix="/products", tags=["products"])


@router.get("")
async def get_products():
    """List all products, by product line and then name."""
    return await ProductService().get_all()


@router.get("/{key}")
async def get_product(key: str):
    """One product, by its id or its slug."""
    product = await ProductService().get(key)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


# Changing products needs the X-Admin-Key header (backend/security.py).

@router.post("", status_code=201, dependencies=[Depends(require_admin)])
async def create_product(product: ProductCreate):
    try:
        return await ProductService().create(product)
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=409, detail="A product with this slug already exists.")


@router.patch("/{key}", dependencies=[Depends(require_admin)])
async def update_product(key: str, changes: ProductUpdate):
    try:
        product = await ProductService().update(key, changes)
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=409, detail="A product with this slug already exists.")
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.delete("/{key}", status_code=204, dependencies=[Depends(require_admin)])
async def delete_product(key: str):
    if not await ProductService().delete(key):
        raise HTTPException(status_code=404, detail="Product not found")
    return Response(status_code=204)
