from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .service import ProductService
from ..schemas import ProductCreate

router = APIRouter(
    prefix="/products",
    tags=["products"]
)

@router.get("")
async def get_products():
    """List all products."""
    service = ProductService()
    return await service.get_all()

@router.get("/{product_id}")
async def get_product(product_id: str):
    """Get a specific product by ID."""
    service = ProductService()
    product = await service.get_by_id(product_id)
    if not product:
        return {"error": "Product not found"} # Handle 404 appropriately in a real app
    return product

@router.post("", status_code=201)
async def create_product(product: ProductCreate):
    """Create a new product (Admin function mostly)."""
    service = ProductService()
    return await service.create(product)
