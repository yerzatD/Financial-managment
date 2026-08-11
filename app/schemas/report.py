from pydantic import BaseModel
from datetime import date


class ReportRequest(BaseModel):
    # Optional date range filter. If both are None, the whole history is used.
    date_from: date | None = None
    date_to: date | None = None


class ReportResponse(BaseModel):
    report: str
    transactions_analyzed: int
    period_from: date | None = None
    period_to: date | None = None