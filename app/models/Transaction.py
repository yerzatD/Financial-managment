from ..database import Base
from sqlalchemy import String, Integer, Column, ForeignKey, Float,DateTime,Boolean
from datetime import datetime
from sqlalchemy.orm import relationship

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)
    type = Column(String, nullable=False)  
    status = Column(String, nullable=False,default="Finished")
    category = Column(String, nullable=True)
    description = Column(String, nullable=True)
    spent_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="transactions")