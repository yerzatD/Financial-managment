from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..database import get_db
from ..models.User import User
from ..schemas.deposit import DepositCreate, DepositResponse, DepositUpdate
from ..services.deposit_service import DepositService

router = APIRouter(prefix="/deposits", tags=["deposits"])


def get_deposit_service(db: Session = Depends(get_db)) -> DepositService:
    return DepositService(db)


@router.post("/", response_model=DepositResponse, status_code=status.HTTP_201_CREATED)
def create_deposit(
    data: DepositCreate,
    current_user: User = Depends(get_current_user),
    service: DepositService = Depends(get_deposit_service),
):
    return service.create_deposit(current_user.id, data)


@router.get("/", response_model=list[DepositResponse])
def get_all_deposits(
    current_user: User = Depends(get_current_user),
    service: DepositService = Depends(get_deposit_service),
):
    return service.get_all_deposits(current_user.id)


@router.get("/{deposit_id}", response_model=DepositResponse)
def get_deposit(
    deposit_id: int,
    current_user: User = Depends(get_current_user),
    service: DepositService = Depends(get_deposit_service),
):
    return service.get_deposit(current_user.id, deposit_id)


@router.put("/{deposit_id}", response_model=DepositResponse)
def update_deposit(
    deposit_id: int,
    data: DepositUpdate,
    current_user: User = Depends(get_current_user),
    service: DepositService = Depends(get_deposit_service),
):
    return service.update_deposit(current_user.id, deposit_id, data)


@router.delete("/{deposit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_deposit(
    deposit_id: int,
    current_user: User = Depends(get_current_user),
    service: DepositService = Depends(get_deposit_service),
):
    service.delete_deposit(current_user.id, deposit_id)
    return None