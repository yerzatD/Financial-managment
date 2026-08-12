from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class ReportRequest(BaseModel):
    date_from: date | None = None
    date_to: date | None = None


class ReportResponse(BaseModel):
    report: str
    transactions_analyzed: int
    period_from: date | None = None
    period_to: date | None = None


class ReportHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    report: str = Field(validation_alias="report_text")
    transactions_analyzed: int
    period_from: date | None = None
    period_to: date | None = None
    created_at: datetime