from pydantic import BaseModel, EmailStr,ConfigDict
from typing import Optional

class UserBase(BaseModel):
    username: str
    email: EmailStr
    password: str
    avatar: Optional[str] = None

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    avatar: Optional[str] = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    email: EmailStr
    avatar: Optional[str] = None
    balance: float
