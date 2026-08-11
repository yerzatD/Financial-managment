from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime
from .enum import *

class TransactionBase(BaseModel):
    amount: float
    type: TypeOfTransaction
    category: Category | None
    description: Optional[str] = None
    spent_at : datetime

class CreateTransaction(TransactionBase):
    pass

class TransactionUpdate(BaseModel):
    amount: Optional[float] = None
    type: TypeOfTransaction = None
    category: Category = None
    description: Optional[str] = None
    spent_at : Optional[datetime] = None

    
class TransactionResponse(TransactionBase):
    model_config = ConfigDict(from_attributes=True)
    pass