from ..database import Base
from sqlalchemy import String, Integer, Column, ForeignKey, Float,DateTime,Boolean
from datetime import datetime
from sqlalchemy.orm import relationship

class AIMessage(Base):
    __tablename__ = "message"

    id = Column(Integer,primary_key=True,index=True)
    conversation_id = Column(Integer,ForeignKey("chats.id"))
    role = Column(String)
    content = Column(String)
    created_at = Column(DateTime,default=datetime.utcnow)

    conversation = relationship("AIConversation", back_populates="messages")
