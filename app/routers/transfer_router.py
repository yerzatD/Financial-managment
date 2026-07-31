# routers/transfer_router.py
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..auth import get_current_user
from ..models.User import User
from ..schemas.transactions import TransferCreate, TransactionResponse
from ..services.transfer_service import TransferService

router = APIRouter(prefix="/api/transfers", tags=["transfers"])


def get_transfer_service(db: AsyncSession = Depends(get_db)) -> TransferService:
    return TransferService(db)


@router.post("/", response_model=TransactionResponse)
async def transfer_money(
    data: TransferCreate,
    current_user: User = Depends(get_current_user),
    service: TransferService = Depends(get_transfer_service),
):
    return await service.transfer_money(current_user.id, data)


@router.get("/history", response_model=List[TransactionResponse])
async def get_history(
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    service: TransferService = Depends(get_transfer_service),
):
    return await service.get_history(current_user.id, limit=limit, offset=offset)