# services/deposit_service.py
from ..repositories.account_repository import AccountRepository
from ..repositories.transaction_repository import TransactionRepository
from ..schemas.deposit import DepositCreate, DepositResponse
from ..repositories.deposit_repository import DepositRepository
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone

class DepositService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.account_repository = AccountRepository(db)
        self.deposit_repository = DepositRepository(db)
        self.transaction_repository = TransactionRepository(db)

    async def open_deposit(self, user_id: int, data: DepositCreate) -> DepositResponse:
        account = await self.account_repository.get_by_user_id(user_id)
        if account is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")

        rate = 0.10 if data.term_months < 6 else 0.15

        withdrawn = await self.account_repository.withdraw(account.id, data.amount)
        if not withdrawn:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient funds")

        deposit = await self.deposit_repository.create_deposit(
            account_id=account.id,
            principal=data.amount,
            rate=rate,
            term_months=data.term_months,
        )

        await self.transaction_repository.create_transaction(
            from_account_id=account.id,
            to_account_id=None,
            amount=data.amount,
            type="deposit_topup",
            status="completed",
            description=f"Открытие вклада на {data.term_months} мес.",
        )

        return DepositResponse.model_validate(deposit)

    async def accrue_interest(self) -> None:
        deposits = await self.deposit_repository.get_active_deposits()
        now = datetime.now(timezone.utc)

        for deposit in deposits:
            if deposit.end_date <= now:
                # Pay final interest BEFORE closing
                interest = deposit.principal * deposit.rate / 12
                await self.account_repository.adjust_balance(deposit.account_id, interest)

                await self.transaction_repository.create_transaction(
                    from_account_id=None,
                    to_account_id=deposit.account_id,
                    amount=interest,
                    type="deposit_interest",
                    status="completed",
                    description="Начисление процентов по вкладу (финальное)",
                )

                # Close deposit and return principal
                await self.deposit_repository.close_deposit(deposit.id, "closed")
                await self.account_repository.adjust_balance(deposit.account_id, deposit.principal)

                await self.transaction_repository.create_transaction(
                    from_account_id=None,
                    to_account_id=deposit.account_id,
                    amount=deposit.principal,
                    type="deposit_close",
                    status="completed",
                    description="Закрытие вклада, возврат тела вклада",
                )
            else:
                interest = deposit.principal * deposit.rate / 12
                await self.account_repository.adjust_balance(deposit.account_id, interest)

                await self.transaction_repository.create_transaction(
                    from_account_id=None,
                    to_account_id=deposit.account_id,
                    amount=interest,
                    type="deposit_interest",
                    status="completed",
                    description="Начисление процентов по вкладу",
                )