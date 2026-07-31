from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from ..auth import hash_password
from ..models.User import User
from ..schemas.user import UserCreate,UserUpdate

class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, user_create: UserCreate) -> User:
        new_user = User(
            username=user_create.username,
            phone=user_create.phone,
            email=user_create.email,
            hashed_password=hash_password(user_create.password),
        )
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user

    async def get_user_by_email(self,email : str)-> Optional[User]:
        user = await self.db.execute(select(User).where(User.email == email))
        return user.scalar_one_or_none()
        

    async def get_user_by_number(self,phone : str)-> Optional[User]:
        user = await self.db.execute(select(User).where(User.phone == phone))
        return user.scalar_one_or_none()
        

    async def get_me(self,user_id : int) -> Optional[User]:
        user = await self.db.execute(select(User).where(User.id == user_id))
        return user.scalar_one_or_none()

    async def update_info(self,user_id : int,user_update : UserUpdate):
        user = await self.db.get(User, user_id)
        if user is None:
            return None

        if user_update.username is not None:
            user.username = user_update.username
        if user_update.email is not None:
            user.email = user_update.email
        if user_update.phone is not None:
            user.phone = user_update.phone
        if user_update.password is not None:
            user.hashed_password = hash_password(user_update.password)
        if user_update.avatar is not None:
            user.avatar = user_update.avatar

        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user


    async def get_by_username(self,username : str) -> Optional[User]:
            user = await self.db.execute(select(User).where(User.username == username))
            return user.scalar_one_or_none()
    

    

