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
        if data.type == "income":
            user.balance += data.amount

        if data.type == "expense":
            user.balance -= data.amount
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        return TransactionResponse.model_validate(transaction)


    def update_transaction(self, user_id : int, data : TransactionUpdate) -> TransactionResponse:
        updated = Transaction(
            user_id = user_id,
            amount = data.amount,
            type = data.type,
            category = data.category,
            description = data.description,
            spent_at = data.spent_at,
            )

        self.db.add(updated)
        self.db.commit()
        self.db.refresh(updated)
        return TransactionResponse.model_validate(updated)

    def get_all_transaction(self,user_id : int) -> list[TransactionResponse]:
        transactions = self.db.query(Transaction).filter(Transaction.user_id == user_id).all()
        if transactions is None:
            raise HTTPException(status_code=404, detail="Transactions not found")
        return List(TransactionResponse.model_validate(tran) for tran in transactions)

    def get_transaction_by_category(self,user_id:int,category:Category) -> list(TransactionResponse):
        transactions = self.db.query(Transaction).filter((Transaction.user_id == user_id)and(Transaction.category == category)).all()
        return List(TransactionResponse.model_validate(tran) for tran in transactions)

    def get_transaction_by_type(self,user_id : int, type : TypeOfTransaction):
        transactions = self.db.query(Transaction).filter((Transaction.user_id == user_id)and(Transaction.type == type)).all()
        return List(TransactionResponse.model_validate(tran) for tran in transactions)

    