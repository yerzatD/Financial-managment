from fastapi import APIRouter, Depends
from ..services.transaction_service import TransactionService
from ..schemas.transaction import *
from ..auth import get_current_user
from ..models.User import User
from ..models.Transaction import Transaction
from sqlalchemy.orm import Session
from ..database import get_db


router = APIRouter(prefix="/api/transactions", tags=["Transactions"])

def get_transaction_service(db: Session = Depends(get_db)) -> TransactionService:
    return TransactionService(db)

@router.post("/create",response_model=TransactionResponse)
def create_transaction(data : CreateTransaction,user : User = Depends(get_current_user),service: TransactionService = Depends(get_transaction_service)):

    return service.create_transaction(user.id,data=data)

 