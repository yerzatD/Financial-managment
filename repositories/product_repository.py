from typing import Optional, Sequence, List
from datetime import datetime, timedelta

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.Product import Product


class ProductRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> List[Product]:
        products = await self.db.execute(select(Product))
        return products.scalars().all()

    async def get_by_id(self, product_id: int) -> Optional[Product]:
        product = await self.db.execute(select(Product).where(Product.id == product_id))
        return product.scalar_one_or_none()

    async def decrease_stock(self, product_id: int, quantity: int) -> bool:
        result = await self.db.execute(
            update(Product)
            .where(Product.id == product_id, Product.stock >= quantity)
            .values(stock=Product.stock - quantity)
        )
        await self.db.commit()
        return result.rowcount > 0