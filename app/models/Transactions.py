from ..database import Base
from sqlalchemy import String, Integer, Column, ForeignKey, Float,DateTime,Boolean
from datetime import datetime
from sqlalchemy.orm import relationship

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer,primary_key=True,index=True)
    from_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)
    to_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)
    amount = Column(Float)
    type = Column(String)
    status = Column(String)
    idempotency_key = Column(String, unique=True, nullable=True, index=True)
    description = Column(String,nullable=True)
    created_at = Column(DateTime,default=datetime.utcnow)