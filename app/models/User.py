from ..database import Base
from sqlalchemy import String, Integer, Column, ForeignKey, Float,DateTime,Boolean
from datetime import datetime
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(Integer,primary_key=True,index=True)
    username = Column(String,unique=True,index=True, nullable=False)
    email = Column(String,nullable=False,unique=True)
    hashed_password = Column(String,nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    avatar = Column(String, nullable=True,default="default_avatar.png")
    balance = Column(Float, default=0.0)
    role = Column(String, default="user")
    
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")

