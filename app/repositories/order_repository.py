from typing import Optional, Sequence, List
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.Order import Order
from ..models.OrderItem import OrderItem


class OrderItemData:
    """Простой контейнер для передачи данных одного товара в заказе."""
    def __init__(self, product_id: int, quantity: int, price_at_purchase: float):
        self.product_id = product_id
        self.quantity = quantity
        self.price_at_purchase = price_at_purchase


class OrderRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_order(
        self,
        user_id: int,
        items: List[OrderItemData],
        total_amount: float,
    ) -> Order:
        order = Order(
            user_id=user_id,
            total_amount=total_amount,
            status="created",
        )
        self.db.add(order)
        await self.db.flush()

        for item in items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                price_at_purchase=item.price_at_purchase,
            )
            self.db.add(order_item)

        await self.db.commit()
        await self.db.refresh(order)
        return order

    async def get_by_id(self, order_id: int) -> Optional[Order]:
        result = await self.db.execute(
            select(Order)
            .options(selectinload(Order.items))
            .where(Order.id == order_id)
        )
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: int) -> Sequence[Order]:
        result = await self.db.execute(
            select(Order)
            .options(selectinload(Order.items))
            .where(Order.user_id == user_id)
            .order_by(Order.created_at.desc())
        )
        return result.scalars().all()

    async def update_status(self, order_id: int, new_status: str) -> Optional[Order]:
        order = await self.db.get(Order, order_id)
        if order is None:
            return None

        order.status = new_status
        self.db.add(order)
        await self.db.commit()
        await self.db.refresh(order)
        return order