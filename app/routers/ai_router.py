from fastapi import APIRouter, Depends
from ..services.ai_service import AIService
from ..schemas.report import ReportRequest, ReportResponse, ReportHistoryResponse
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


@router.get("/", response_model=list[ReportHistoryResponse])
def list_reports(
    current_user: User = Depends(get_current_user),
    ai_service: AIService = Depends(AIService),
):
    return ai_service.get_report_history(current_user.id)


@router.get("/{report_id}", response_model=ReportHistoryResponse)
def get_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    ai_service: AIService = Depends(AIService),
):
    return ai_service.get_report_by_id(current_user.id, report_id)