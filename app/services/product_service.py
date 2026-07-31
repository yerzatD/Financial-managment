from ..repositories.product_repository import ProductRepository
from ..schemas.product import ProductResponse
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional,List

class ProductService:
    def __init__(self,db : AsyncSession):
        self.db = db
        self.product_repository = ProductRepository(db)

    async def list_products(self) -> List[ProductResponse]:
        products = await self.product_repository.get_all()
        return [ProductResponse.model_validate(product) for product in products]

    async def get_product(self,product_id : int) -> ProductResponse:
        product = await self.product_repository.get_by_id(product_id)
        if product is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Product not found")
        return ProductResponse.model_validate(product)

    