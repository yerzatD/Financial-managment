from datetime import date

from pydantic import BaseModel, ConfigDict, model_validator

from .enum import Category


class DepositBase(BaseModel):
    name: str
    category: Category | None = None
    limit_amount: float
    start_date: date
    end_date: date

    @model_validator(mode="after")
    def check_dates(self):
        if self.end_date <= self.start_date:
            raise ValueError("end_date must be after start_date")
        if self.limit_amount <= 0:
            raise ValueError("limit_amount must be positive")
        return self


class DepositCreate(DepositBase):
    pass


class DepositUpdate(BaseModel):
    name: str | None = None
    category: Category | None = None
    limit_amount: float | None = None
    start_date: date | None = None
    end_date: date | None = None


class DepositResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    category: Category | None = None
    limit_amount: float
    start_date: date
    end_date: date
    spent_amount: float
    remaining_amount: float
    is_exceeded: bool