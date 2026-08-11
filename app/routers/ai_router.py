from fastapi import APIRouter, Depends
from ..services.ai_service import AIService
from ..schemas.report import ReportRequest, ReportResponse
from ..auth import get_current_user
from ..models.User import User

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.post("/", response_model=ReportResponse)
def get_ai_report(
    request: ReportRequest,
    current_user: User = Depends(get_current_user),
    ai_service: AIService = Depends(AIService),
):
    return ai_service.generate_report(current_user, request)