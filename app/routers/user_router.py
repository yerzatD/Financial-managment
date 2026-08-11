from fastapi import APIRouter, Depends
from ..services.user_service import UserService
from ..schemas.user import *
from ..auth import get_current_user
from ..models.User import User
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ..database import get_db

router = APIRouter(prefix="/api/users",tags=["Users"])

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)


@router.post("/register", response_model=UserResponse)
def register(data: UserCreate, service: UserService = Depends(get_user_service)):
    return service.register_user(data)


@router.post("/token", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: UserService = Depends(get_user_service),
):
    return service.login_user(form_data)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)


@router.patch("/me", response_model=UserResponse)
def update_me(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    return service.update_user(data, current_user)