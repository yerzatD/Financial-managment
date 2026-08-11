from ..schemas.transaction import *
from ..models.Transaction import Transaction
from ..database import get_db
from ..models.User import User
from sqlalchemy.orm import Session
from fastapi import Depends,HTTPException,status
from typing import List
from ..schemas.enum import Category,TypeOfTransaction


class TransactionService:
    def __init__(self,db : Session = Depends(get_db)):
        self.db = db

    def create_transaction(self,user_id : int,data : CreateTransaction) -> TransactionResponse:
        transaction = Transaction(
            user_id = user_id,
            amount = data.amount,
            type = data.type,
            category = data.category,
            description = data.description,
            spent_at = data.spent_at,
            )
        user = self.db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        if data.type == TypeOfTransaction.INCOME:
            user.balance += data.amount
        elif data.type == TypeOfTransaction.EXPENSE:
            user.balance -= data.amount
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        return TransactionResponse.model_validate(transaction)


    def update_transaction(self, user_id: int, transaction_id: int, data: TransactionUpdate) -> TransactionResponse:
        transaction = self.db.query(Transaction).filter(
            Transaction.id == transaction_id, Transaction.user_id == user_id
        ).first()
        if transaction is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

        user = self.db.query(User).filter(User.id == user_id).first()

        if transaction.type == TypeOfTransaction.INCOME:
            user.balance -= transaction.amount
        elif transaction.type == TypeOfTransaction.EXPENSE:
            user.balance += transaction.amount

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(transaction, field, value)

        if transaction.type == TypeOfTransaction.INCOME:
            user.balance += transaction.amount
        elif transaction.type == TypeOfTransaction.EXPENSE:
            user.balance -= transaction.amount

        self.db.commit()
        self.db.refresh(transaction)
        return TransactionResponse.model_validate(transaction)

    def get_all_transaction(self,user_id : int) -> list[TransactionResponse]:
        transactions = self.db.query(Transaction).filter(Transaction.user_id == user_id).all()
        return [TransactionResponse.model_validate(tran) for tran in transactions]

    def get_transaction_by_category(self,user_id:int,category:Category):
        transactions = self.db.query(Transaction).filter(Transaction.user_id == user_id,Transaction.category == category).all()
        return [TransactionResponse.model_validate(tran) for tran in transactions]

    def get_transaction_by_type(self,user_id : int, type : TypeOfTransaction):
        transactions = self.db.query(Transaction).filter(Transaction.user_id == user_id,Transaction.type == type).all()
        return [TransactionResponse.model_validate(tran) for tran in transactions]

    