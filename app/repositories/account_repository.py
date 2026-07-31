from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.Account import Account
from ..schemas.account import AccountBalance

class AccountRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_account(self, user_id: int, currency_type: str = "KZT") -> Account:
        new_account = Account(
            currency_type=currency_type,
            user_id=user_id,
            balance=0.0,
        )
        self.db.add(new_account)
        await self.db.commit()
        await self.db.refresh(new_account)
        return new_account

    async def get_by_id(self, account_id: int) -> Account | None:
        account = await self.db.execute(select(Account).where(Account.id == account_id))
        return account.scalar_one_or_none()

    async def get_by_user_id(self, user_id: int) -> Account | None:
        account = await self.db.execute(select(Account).where(Account.user_id == user_id))
        return account.scalar_one_or_none()

    async def withdraw(self, account_id: int, amount: float) -> bool:
        result = await self.db.execute(
            update(Account)
            .where(Account.id == account_id, Account.balance >= amount)
            .values(balance=Account.balance - amount)
        )
        await self.db.commit()
        return result.rowcount > 0

    async def adjust_balance(self, account_id: int, delta: float) -> Account | None:
        await self.db.execute(
            update(Account)
            .where(Account.id == account_id)
            .values(balance=Account.balance + delta)
        )
        await self.db.commit()
        return await self.get_by_id(account_id)

    async def get_balance(self, account_id: int) -> float | None:
        account = await self.db.execute(select(Account).where(Account.id == account_id))
        result = account.scalar_one_or_none()
        if result is None:
            return None
        return result.balance

    async def add_money(self, account_id: int, amount: float) -> Account | None:
        account = await self.get_by_id(account_id)
        if account is None:
            return None
        account.balance += amount
        self.db.add(account)
        await self.db.commit()
        await self.db.refresh(account)
        return account