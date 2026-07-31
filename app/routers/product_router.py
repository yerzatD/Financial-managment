# routers/product_router.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ..database import get_db
from ..schemas.product import ProductResponse
from ..services.product_service import ProductService

router = APIRouter(prefix="/api/products", tags=["products"])


def get_product_service(db: AsyncSession = Depends(get_db)) -> ProductService:
    return ProductService(db)


@router.get("/", response_model=List[ProductResponse])
async def list_products(service: ProductService = Depends(get_product_service)):
    return await service.list_products()


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, service: ProductService = Depends(get_product_service)):
    return await service.get_product(product_id)