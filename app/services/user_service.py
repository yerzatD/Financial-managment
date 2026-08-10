from ..schemas.user import *
from ..models.User import User
from ..database import get_db
from ..auth import get_current_user,hash_password,verify_access_token,verify_password,create_access_token
from sqlalchemy.orm import Session
from fastapi import Depends,HTTPException,status
from fastapi.security import OAuth2PasswordRequestForm
from typing import List


class UserService:
    def __init__(self,db:Session = Depends(get_db)):
        self.db = db


    def register_user(self,data : UserCreate) -> UserResponse:
        existing = self.db.query(User).filter(User.email == data.email).first()
        existing1 = self.db.query(User).filter(User.username == data.username).first()
        if existing is not None or existing1 is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="User already registred")
        user = User(
            useername = data.username,
            email = data.email,
            hashed_password=hash_password(data.password),
            avatar = data.avatar,
        )

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return UserResponse.model_validate(user)

    def login_user(self,form_data : OAuth2PasswordRequestForm) -> Token:
        user = self.db.query(User).filter(User.username == form_data.username)
        if user is None or not verify_password(form_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token = create_access_token(data={"sub" : str(user.id)})
        return Token.model_validate(access_token = access_token, token_type ="bearer")


    def update_user(self, user_id: int, user_update: UserUpdate) -> UserResponse:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        existing_email = self.db.query(User).filter(User.email == user_update.email).first() if user_update.email else None
        if existing_email and existing_email.id != user_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

        existing_username = self.db.query(User).filter(User.username == user_update.username).first() if user_update.username else None
        if existing_username and existing_username.id != user_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")

        if user_update.email:
            user.email = user_update.email
        if user_update.username:
            user.username = user_update.username
        if user_update.password:
            hashed_password = hash_password(user_update.password)
            user.hashed_password = hashed_password
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return UserResponse.model_validate(user)

    def get_me(self, user_id: int) -> UserResponse:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return UserResponse.model_validate(user)


    def get_all_users(self,user_id : int) -> list[UserResponse]:
        Users = self.db.query(User).all()
        return List(user for user in Users)
        
    