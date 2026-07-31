from ..database import Base
from sqlalchemy import String, Integer, Column, ForeignKey, Float,DateTime,Boolean
from datetime import datetime
from sqlalchemy.orm import relationship

class AIConversation(Base):
    __tablename__ = "chats"

    id = Column(Integer,primary_key=True,index=True)
    user_id = Column(Integer,ForeignKey("users.id"))
    created_at = Column(DateTime,default=datetime.utcnow)

    messages = relationship("AIMessage", back_populates="conversation")