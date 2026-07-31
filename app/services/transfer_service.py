# services/transfer_service.py
from typing import List

from ..repositories.account_repository import AccountRepository
from ..repositories.transaction_repository import TransactionRepository
from ..repositories.user_repository import UserRepository
from ..schemas.transactions import TransferCreate, TransactionResponse

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession


class TransferService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.account_repository = AccountRepository(db)
        self.transaction_repository = TransactionRepository(db)
        self.user_repository = UserRepository(db)

    async def transfer_money(self, from_user_id: int, data: TransferCreate) -> TransactionResponse:
        from_account = await self.account_repository.get_by_user_id(from_user_id)
        if from_account is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sender account not found")

        existing = await self.transaction_repository.get_by_idempotency_key(data.idempotency_key)
        if existing is not None:
            if existing.from_account_id != from_account.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Idempotency key belongs to another user",
                )
            return TransactionResponse.model_validate(existing)

        to_user = await self.user_repository.get_user_by_number(data.to_phone)
        if to_user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipient not found")

        if to_user.id == from_user_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot transfer to your own account")

        to_account = await self.account_repository.get_by_user_id(to_user.id)
        if to_account is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipient account not found")

        withdrawn = await self.account_repository.withdraw(from_account.id, data.amount)
        if not withdrawn:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient funds")

        await self.account_repository.adjust_balance(to_account.id, data.amount)

        transaction = await self.transaction_repository.create_transaction(
            from_account_id=from_account.id,
            to_account_id=to_account.id,
            amount=data.amount,
            type="transfer",
            status="completed",
            description=data.description,
            idempotency_key=data.idempotency_key,
        )

        return TransactionResponse.model_validate(transaction)

    async def get_history(
        self, user_id: int, limit: int = 50, offset: int = 0
    ) -> List[TransactionResponse]:
        account = await self.account_repository.get_by_user_id(user_id)
        if account is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")

        histories = await self.transaction_repository.get_history_by_account(
            account.id, limit=limit, offset=offset
        )
        return [TransactionResponse.model_validate(history) for history in histories]