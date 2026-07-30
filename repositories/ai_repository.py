from typing import Optional, Sequence, List
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.AIConversation import AIConversation
from ..models.AIMessage import AIMessage


class AIRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # --- Conversation ---

    async def create_conversation(self, user_id: int) -> AIConversation:
        conversation = AIConversation(user_id=user_id)
        self.db.add(conversation)
        await self.db.commit()
        await self.db.refresh(conversation)
        return conversation

    async def get_conversation_by_id(self, conversation_id: int) -> Optional[AIConversation]:
        result = await self.db.execute(
            select(AIConversation).where(AIConversation.id == conversation_id)
        )
        return result.scalar_one_or_none()

    async def get_conversations_by_user(self, user_id: int) -> Sequence[AIConversation]:
        result = await self.db.execute(
            select(AIConversation)
            .where(AIConversation.user_id == user_id)
            .order_by(AIConversation.created_at.desc())
        )
        return result.scalars().all()

    # --- Messages ---

    async def add_message(self, conversation_id: int, role: str, content: str) -> AIMessage:
        message = AIMessage(
            conversation_id=conversation_id,
            role=role,
            content=content,
        )
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)
        return message

    async def get_messages_by_conversation(
        self, conversation_id: int, limit: int = 20
    ) -> Sequence[AIMessage]:
        result = await self.db.execute(
            select(AIMessage)
            .where(AIMessage.conversation_id == conversation_id)
            .order_by(AIMessage.created_at.desc())
            .limit(limit)
        )
        messages = result.scalars().all()
        return list(reversed(messages))  # разворачиваем в хронологический порядок