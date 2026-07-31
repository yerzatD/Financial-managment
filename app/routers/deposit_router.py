# routers/deposit_router.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..auth import get_current_user
from ..models.User import User
from ..schemas.deposit import DepositCreate, DepositResponse
from ..services.deposit_service import DepositService

router = APIRouter(prefix="/api/deposits", tags=["deposits"])


def get_deposit_service(db: AsyncSession = Depends(get_db)) -> DepositService:
    return DepositService(db)


@router.post("/", response_model=DepositResponse)
async def open_deposit(
    data: DepositCreate,
    current_user: User = Depends(get_current_user),
    service: DepositService = Depends(get_deposit_service),
):
    return await service.open_deposit(current_user.id, data)