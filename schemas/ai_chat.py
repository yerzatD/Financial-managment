from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List

class AIChatRequest(BaseModel):
    message: str
    conversation_id: Optional[int] = None

class AIMessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    role: str
    content: str
    created_at: datetime

class AIChatResponse(BaseModel):
    conversation_id: int
    reply: str

class AIConversationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    messages: List[AIMessageResponse]