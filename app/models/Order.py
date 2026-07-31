from ..database import Base
from sqlalchemy import String, Integer, Column, ForeignKey, Float,DateTime,Boolean
from datetime import datetime
from sqlalchemy.orm import relationship

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer,primary_key=True, index=True)
    user_id = Column(Integer,ForeignKey("users.id"))
    total_amount = Column(Float)
    status = Column(String)
    created_at = Column(DateTime,default=datetime.utcnow)

    items = relationship("OrderItem", back_populates="order")