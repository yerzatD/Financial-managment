# routers/account_router.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ..schemas.account import AccountBalance
from ..database import get_db
from ..auth import get_current_user
from ..models.User import User
from ..schemas.account import AccountResponse
from ..services.account_service import AccountService

router = APIRouter(prefix="/api/accounts", tags=["accounts"])


def get_account_service(db: AsyncSession = Depends(get_db)) -> AccountService:
    return AccountService(db)


@router.get("/me", response_model=AccountResponse)
async def get_my_account(
    current_user: User = Depends(get_current_user),
    service: AccountService = Depends(get_account_service),
):
    return await service.get_my_account(current_user.id)


@router.get("/me/balance")
async def get_my_balance(
    current_user: User = Depends(get_current_user),
    service: AccountService = Depends(get_account_service),
):
    account = await service.get_my_account(current_user.id)
    balance = await service.get_balance(account.id)
    return {"balance": balance}


@router.put("/add", response_model=AccountBalance)
async def add_money(
    amount: float,
    current_user: User = Depends(get_current_user),
    service: AccountService = Depends(get_account_service),
):
    return await service.add_money(user_id=current_user.id, amount=amount)