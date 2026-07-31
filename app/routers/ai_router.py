# routers/ai_router.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..auth import get_current_user
from ..models.User import User
from ..schemas.ai_chat import AIChatRequest, AIChatResponse
from ..services.ai_service import AIAssistantService

router = APIRouter(prefix="/api/ai", tags=["ai"])


def get_ai_service(db: AsyncSession = Depends(get_db)) -> AIAssistantService:
    return AIAssistantService(db)


@router.post("/chat", response_model=AIChatResponse)
async def chat(
    data: AIChatRequest,
    current_user: User = Depends(get_current_user),
    service: AIAssistantService = Depends(get_ai_service),
):
    try:
        return await service.chat(current_user.id, data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/analyze", response_model=AIChatResponse)
async def analyze_spending(
    current_user: User = Depends(get_current_user),
    service: AIAssistantService = Depends(get_ai_service),
):
    return await service.analyze_spending(current_user.id)