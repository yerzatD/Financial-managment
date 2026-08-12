from datetime import date, datetime

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.Deposit import Deposit
from ..models.Transaction import Transaction
from ..schemas.deposit import DepositCreate, DepositResponse, DepositUpdate
from ..schemas.enum import TypeOfTransaction


class DepositService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def _spent_amount(self, user_id: int, deposit: Deposit) -> float:
        query = self.db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.type == TypeOfTransaction.EXPENSE,
            Transaction.spent_at >= datetime.combine(deposit.start_date, datetime.min.time()),
            Transaction.spent_at <= datetime.combine(deposit.end_date, datetime.max.time()),
        )
        if deposit.category:
            query = query.filter(Transaction.category == deposit.category)
        return sum(t.amount for t in query.all())

    def _to_response(self, user_id: int, deposit: Deposit) -> DepositResponse:
        spent = self._spent_amount(user_id, deposit)
        return DepositResponse(
            id=deposit.id,
            name=deposit.name,
            category=deposit.category,
            limit_amount=deposit.limit_amount,
            start_date=deposit.start_date,
            end_date=deposit.end_date,
            spent_amount=spent,
            remaining_amount=deposit.limit_amount - spent,
            is_exceeded=spent > deposit.limit_amount,
        )

    def create_deposit(self, user_id: int, data: DepositCreate) -> DepositResponse:
        deposit = Deposit(
            user_id=user_id,
            name=data.name,
            category=data.category,
            limit_amount=data.limit_amount,
            start_date=data.start_date,
            end_date=data.end_date,
        )
        self.db.add(deposit)
        self.db.commit()
        self.db.refresh(deposit)
        return self._to_response(user_id, deposit)

    def get_all_deposits(self, user_id: int) -> list[DepositResponse]:
        deposits = self.db.query(Deposit).filter(Deposit.user_id == user_id).all()
        return [self._to_response(user_id, d) for d in deposits]

    def get_deposit(self, user_id: int, deposit_id: int) -> DepositResponse:
        deposit = self.db.query(Deposit).filter(
            Deposit.id == deposit_id, Deposit.user_id == user_id
        ).first()
        if deposit is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deposit not found")
        return self._to_response(user_id, deposit)

    def update_deposit(self, user_id: int, deposit_id: int, data: DepositUpdate) -> DepositResponse:
        deposit = self.db.query(Deposit).filter(
            Deposit.id == deposit_id, Deposit.user_id == user_id
        ).first()
        if deposit is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deposit not found")

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(deposit, field, value)

        self.db.commit()
        self.db.refresh(deposit)
        return self._to_response(user_id, deposit)

    def delete_deposit(self, user_id: int, deposit_id: int) -> None:
        deposit = self.db.query(Deposit).filter(
            Deposit.id == deposit_id, Deposit.user_id == user_id
        ).first()
        if deposit is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deposit not found")
        self.db.delete(deposit)
        self.db.commit()

    def get_active_deposits(self, user_id: int, on_date: date | None = None) -> list[Deposit]:
        on_date = on_date or date.today()
        return self.db.query(Deposit).filter(
            Deposit.user_id == user_id,
            Deposit.start_date <= on_date,
            Deposit.end_date >= on_date,
        ).all()