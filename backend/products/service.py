import uuid

from sqlalchemy import select

from ..database import session
from ..models import Product
from ..schemas import ProductCreate, ProductUpdate
from .serializer import ProductSerializer


class ProductService:
    async def get_all(self):
        # a stable order (line, then name), so the list does not reshuffle after every edit
        result = await session.execute(select(Product).order_by(Product.category_slug, Product.name))
        return ProductSerializer(many=True).dump(result.scalars().all())

    async def _find(self, key: str) -> Product | None:
        """A product by its id, or by its slug when the key is not an id."""
        try:
            where = Product.id == uuid.UUID(key)
        except ValueError:
            where = Product.slug == key
        result = await session.execute(select(Product).where(where))
        return result.scalars().first()

    async def get(self, key: str):
        product = await self._find(key)
        return ProductSerializer().dump(product) if product else None

    async def create(self, data: ProductCreate):
        product = Product(**data.model_dump())
        session.add(product)
        await session.commit()
        await session.refresh(product)
        return ProductSerializer().dump(product)

    async def update(self, key: str, data: ProductUpdate):
        product = await self._find(key)
        if not product:
            return None
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(product, field, value)
        await session.commit()
        await session.refresh(product)
        return ProductSerializer().dump(product)

    async def delete(self, key: str) -> bool:
        product = await self._find(key)
        if not product:
            return False
        await session.delete(product)
        await session.commit()
        return True
