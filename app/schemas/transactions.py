from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional

class TransferCreate(BaseModel):
    to_phone: str
    amount: float = Field(gt=0)  # запрещаем 0 и отрицательные переводы
    description: Optional[str] = None
    idempotency_key: str


class TransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    from_account_id: Optional[int]
    to_account_id: Optional[int]
    amount: float
    type: str
    status: str
    description: Optional[str]
    created_at: datetime