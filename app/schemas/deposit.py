from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime

class DepositCreate(BaseModel):
    amount: float = Field(gt=0)
    term_months: int = Field(gt=0)

class DepositResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    account_id: int
    principal: float
    rate: float
    start_date: datetime
    end_date: datetime
    status: str