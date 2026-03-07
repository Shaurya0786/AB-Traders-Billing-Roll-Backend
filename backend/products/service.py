from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from ..models import Product
from ..schemas import ProductCreate
from .serializer import ProductSerializer

from ..database import session

class ProductService:
    def __init__(self):
        pass

    async def get_all(self):
        result = await session.execute(select(Product))
        products = result.scalars().all()
        return ProductSerializer(many=True).dump(products)

    async def get_by_slug(self, slug: str):
        result = await session.execute(select(Product).where(Product.slug == slug))
        product = result.scalars().first()
        return ProductSerializer().dump(product) if product else None

    async def get_by_id(self, product_id: str):
        result = await session.execute(select(Product).where(Product.id == product_id))
        product = result.scalars().first()
        return ProductSerializer().dump(product) if product else None

    async def create(self, product_data: ProductCreate) -> Product:
        db_product = Product(**product_data.dict())
        session.add(db_product)
        await session.commit()
        await session.refresh(db_product)
        return ProductSerializer().dump(db_product)
