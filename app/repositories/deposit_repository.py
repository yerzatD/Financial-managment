from typing import Optional, Sequence
from datetime import datetime, timezone, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.Deposit import Deposit


class DepositRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_deposit(
        self, account_id: int, principal: float, rate: float, term_months: int
    ) -> Deposit:
        start = datetime.now(timezone.utc)
        end_date = start + timedelta(days=term_months * 30)

        deposit = Deposit(
            account_id=account_id,
            principal=principal,
            rate=rate,
            start_date=start,
            end_date=end_date,
            status="active",
        )
        self.db.add(deposit)
        await self.db.commit()
        await self.db.refresh(deposit)
        return deposit

    async def get_by_id(self, deposit_id: int) -> Optional[Deposit]:
        result = await self.db.execute(
            select(Deposit).where(Deposit.id == deposit_id)
        )
        return result.scalar_one_or_none()

    async def get_by_account_id(self, account_id: int) -> Sequence[Deposit]:
        result = await self.db.execute(
            select(Deposit).where(Deposit.account_id == account_id)
        )
        return result.scalars().all()

    async def get_active_deposits(self) -> Sequence[Deposit]:
        result = await self.db.execute(
            select(Deposit).where(Deposit.status == "active")
        )
        return result.scalars().all()

    async def close_deposit(self, deposit_id: int, new_status: str) -> Optional[Deposit]:
        deposit = await self.get_by_id(deposit_id)
        if deposit is None:
            return None

        deposit.status = new_status
        self.db.add(deposit)
        await self.db.commit()
        await self.db.refresh(deposit)
        return deposit