from ..database import Base
from sqlalchemy import String, Integer, Column, ForeignKey, Float,DateTime,Boolean
from datetime import datetime
from sqlalchemy.orm import relationship

class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer,primary_key=True,index=True)
    user_id = Column(Integer,ForeignKey("users.id"))
    balance = Column(Float)
    currency_type = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User" , back_populates="accounts")