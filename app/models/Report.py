from datetime import datetime, timezone

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship

from ..database import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    report_text = Column(Text, nullable=False)
    transactions_analyzed = Column(Integer, nullable=False, default=0)

    period_from = Column(Date, nullable=True)
    period_to = Column(Date, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", backref="reports")