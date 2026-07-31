# services/user_service.py
from ..repositories.user_repository import UserRepository
from ..repositories.account_repository import AccountRepository
from typing import List

from fastapi.security import OAuth2PasswordRequestForm
from ..auth import create_access_token, verify_password

from fastapi import HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession

from ..models.User import User
from ..schemas.user import UserCreate, UserResponse, UserUpdate, Token


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repository = UserRepository(db)
        self.account_repository = AccountRepository(db)

    async def register_user(self, data: UserCreate) -> UserResponse:
        existing = await self.user_repository.get_user_by_email(data.email)
        if existing is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already registered")
        existing1 = await self.user_repository.get_user_by_number(data.phone)
        if existing1 is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already registered")
        existing_user = await self.user_repository.get_by_username(data.username)
        if existing_user is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")
        user = await self.user_repository.create_user(data)
        await self.account_repository.create_account(user_id=user.id)
        return UserResponse.model_validate(user)

    async def login_user(self, form_data: OAuth2PasswordRequestForm) -> Token:
        # Try username first, then email, then phone
        user = await self.user_repository.get_by_username(form_data.username)
        if user is None:
            user = await self.user_repository.get_user_by_email(form_data.username)
        if user is None:
            user = await self.user_repository.get_user_by_number(form_data.username)

        if user is None or not verify_password(form_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token = create_access_token(data={"sub": str(user.id)})
        return Token(access_token=access_token, token_type="bearer")

    async def update_user(self, user_update: UserUpdate, current_user: User) -> UserResponse:
        user = await self.user_repository.update_info(current_user.id, user_update)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        return UserResponse.model_validate(user)