from ..database import Base
from sqlalchemy import String, Integer, Column, ForeignKey, Float,DateTime,Boolean
from datetime import datetime
from sqlalchemy.orm import relationship

class Deposit(Base):
    __tablename__ = "deposit"
    id = Column(Integer,primary_key=True,index=True)
    account_id = Column(Integer,ForeignKey("accounts.id"))
    principal = Column(Float)
    rate = Column(Float)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    status = Column(String)

