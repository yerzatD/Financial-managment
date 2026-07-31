from typing import Optional, Sequence
from datetime import datetime

from sqlalchemy import select, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.Transactions import Transaction


class TransactionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_transaction(
        self,
        from_account_id: Optional[int],
        to_account_id: Optional[int],
        amount: float,
        type: str,
        status: str = "completed",
        description: Optional[str] = None,
        idempotency_key: Optional[str] = None,
    ) -> Transaction:
        transaction = Transaction(
            from_account_id=from_account_id,
            to_account_id=to_account_id,
            amount=amount,
            type=type,
            status=status,
            description=description,
            idempotency_key=idempotency_key,
        )
        self.db.add(transaction)
        await self.db.commit()
        await self.db.refresh(transaction)
        return transaction

    async def get_by_id(self, transaction_id: int) -> Optional[Transaction]:
        result = await self.db.execute(
            select(Transaction).where(Transaction.id == transaction_id)
        )
        return result.scalar_one_or_none()

    async def get_by_idempotency_key(self, key: str) -> Optional[Transaction]:
        result = await self.db.execute(
            select(Transaction).where(Transaction.idempotency_key == key)
        )
        return result.scalar_one_or_none()

    async def get_history_by_account(
        self, account_id: int, limit: int = 50, offset: int = 0
    ) -> Sequence[Transaction]:
        result = await self.db.execute(
            select(Transaction)
            .where(
                or_(
                    Transaction.from_account_id == account_id,
                    Transaction.to_account_id == account_id,
                )
            )
            .order_by(Transaction.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()

    async def get_history_by_accounts(
        self,
        account_ids: list[int],
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        type: Optional[str] = None,
    ) -> Sequence[Transaction]:
        conditions = [
            or_(
                Transaction.from_account_id.in_(account_ids),
                Transaction.to_account_id.in_(account_ids),
            )
        ]
        if date_from is not None:
            conditions.append(Transaction.created_at >= date_from)
        if date_to is not None:
            conditions.append(Transaction.created_at <= date_to)
        if type is not None:
            conditions.append(Transaction.type == type)

        result = await self.db.execute(
            select(Transaction)
            .where(and_(*conditions))
            .order_by(Transaction.created_at.desc())
        )
        return result.scalars().all()