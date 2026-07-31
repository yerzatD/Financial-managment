# services/order_service.py
from ..repositories.account_repository import AccountRepository
from ..repositories.product_repository import ProductRepository
from ..repositories.order_repository import OrderRepository, OrderItemData
from ..repositories.transaction_repository import TransactionRepository
from ..schemas.order import OrderCreate, OrderResponse

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession


class OrderService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.account_repository = AccountRepository(db)
        self.product_repository = ProductRepository(db)
        self.order_repository = OrderRepository(db)
        self.transaction_repository = TransactionRepository(db)

    # services/order_service.py
    async def create_order(self, user_id: int, data: OrderCreate) -> OrderResponse:
        account = await self.account_repository.get_by_user_id(user_id)
        if account is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")

        order_items: list[OrderItemData] = []
        total_amount = 0.0

        for item in data.items:
            product = await self.product_repository.get_by_id(item.product_id)
            if product is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Product {item.product_id} not found",
                )
            subtotal = product.price * item.quantity
            total_amount += subtotal
            order_items.append(OrderItemData(
                product_id=product.id,
                quantity=item.quantity,
                price_at_purchase=product.price,
            ))

        decreased: list[OrderItemData] = []
        for oi in order_items:
            ok = await self.product_repository.decrease_stock(oi.product_id, oi.quantity)
            if not ok:
                for done in decreased:
                    await self.product_repository.increase_stock(done.product_id, done.quantity)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Not enough stock for product {oi.product_id}",
                )
            decreased.append(oi)

        withdrawn = await self.account_repository.withdraw(account.id, total_amount)
        if not withdrawn:
            for done in decreased:
                await self.product_repository.increase_stock(done.product_id, done.quantity)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient funds")

        order = await self.order_repository.create_order(
            user_id=user_id,
            items=order_items,
            total_amount=total_amount,
        )

        await self.transaction_repository.create_transaction(
            from_account_id=account.id,
            to_account_id=None,
            amount=total_amount,
            type="purchase",
            status="completed",
            description=f"Заказ #{order.id}",
        )

        await self.order_repository.update_status(order.id, "paid")

        return OrderResponse.model_validate(order)