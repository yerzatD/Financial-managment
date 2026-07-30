from ..database import Base
from sqlalchemy import String, Integer, Column, ForeignKey, Float,DateTime,Boolean
from datetime import datetime
from sqlalchemy.orm import relationship

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer,primary_key=True, index=True)
    name = Column(String,nullable=False)
    description = Column(String,nullable=True)
    price = Column(Float)
    image_url = Column(String)
    stock = Column(Integer)
    created_at = Column(DateTime,default=datetime.utcnow)
