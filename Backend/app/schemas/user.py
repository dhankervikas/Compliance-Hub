from typing import Optional, List
from pydantic import BaseModel
# from pydantic import EmailStr # Disabled to allow .local domains
from datetime import datetime


class UserBase(BaseModel):
    email: str 
    username: str
    full_name: Optional[str] = None
    is_active: Optional[bool] = True
    is_superuser: bool = False
    tenant_id: Optional[str] = "default"
    role: Optional[str] = None
    allowed_frameworks: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None
    allowed_frameworks: Optional[str] = None
    is_active: Optional[bool] = None


class User(UserBase):
    id: int
    role: str
    allowed_frameworks: Optional[str] = None
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None