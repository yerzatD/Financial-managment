from ..repositories.account_repository import AccountRepository
from typing import List

from fastapi import HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from ..schemas.account import AccountBalance,AccountResponse
from ..models.Account import Account

class AccountService:
    def __init__(self,db:AsyncSession):
        self.db = db
        self.account_repository = AccountRepository(db)

    async def get_my_account(self,user_id: int) -> AccountResponse:
        account = await self.account_repository.get_by_user_id(user_id)
        if account is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Account not found")
        return AccountResponse.model_validate(account)

    async def get_balance(self, account_id: int) -> float:
        balance = await self.account_repository.get_balance(account_id)
        if balance is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
        return balance

    async def add_money(self, user_id: int, amount: float) -> AccountBalance:
        if amount <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Amount must be positive")
        account = await self.account_repository.get_by_user_id(user_id)
        if account is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
        updated = await self.account_repository.add_money(account.id, amount)
        return AccountBalance(balance=updated.balance, currency_type=updated.currency_type)
        

    
