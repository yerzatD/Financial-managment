from fastapi import APIRouter, Depends, status
from typing import List
from sqlalchemy.orm import Session
from ..database import get_db
from ..services.transaction_service import TransactionService
from ..schemas.transaction import CreateTransaction, TransactionUpdate, TransactionResponse
from ..schemas.enum import Category, TypeOfTransaction
from ..auth import get_current_user
from ..models.User import User

router = APIRouter(
    prefix="/transactions",
    tags=["transactions"]
)


def get_transaction_service(db: Session = Depends(get_db)) -> TransactionService:
    return TransactionService(db)


@router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(
    transaction_data: CreateTransaction,
    current_user: User = Depends(get_current_user),
    service: TransactionService = Depends(get_transaction_service),
):
    return service.create_transaction(current_user.id, transaction_data)


@router.put("/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    transaction_id: int,
    transaction_data: TransactionUpdate,
    current_user: User = Depends(get_current_user),
    service: TransactionService = Depends(get_transaction_service),
):
    return service.update_transaction(current_user.id, transaction_id, transaction_data)


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    service: TransactionService = Depends(get_transaction_service),
):
    service.delete_transaction(current_user.id, transaction_id)
    return None


@router.get("/", response_model=List[TransactionResponse])
def get_all_transactions(
    current_user: User = Depends(get_current_user),
    service: TransactionService = Depends(get_transaction_service),
):
    return service.get_all_transactions(current_user.id)


@router.get("/history", response_model=List[TransactionResponse])
def get_transaction_history(
    current_user: User = Depends(get_current_user),
    service: TransactionService = Depends(get_transaction_service),
):
    return service.get_all_transactions(current_user.id)


@router.get("/by-category/", response_model=List[TransactionResponse])
def get_transactions_by_category(
    category: Category,
    current_user: User = Depends(get_current_user),
    service: TransactionService = Depends(get_transaction_service),
):
    return service.get_transaction_by_category(current_user.id, category)


@router.get("/by-type/", response_model=List[TransactionResponse])
def get_transactions_by_type(
    type: TypeOfTransaction,
    current_user: User = Depends(get_current_user),
    service: TransactionService = Depends(get_transaction_service),
):
    return service.get_transaction_by_type(current_user.id, type)


@router.get("/summary/")
def get_transaction_summary(
    current_user: User = Depends(get_current_user),
    service: TransactionService = Depends(get_transaction_service),
):
    return service.get_transaction_summary(current_user.id)