from datetime import datetime
from typing import List, TYPE_CHECKING, Optional

from passlib.context import CryptContext
from pydantic import BaseModel, validator

from src.accounts.schemas import AccountResponse

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserBase(BaseModel):
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    description: Optional[str] = None
    telegram_chat_id: Optional[int] = None
    telegram_username: Optional[str] = None
    phone_number: Optional[str] = None
    email_address: Optional[str] = None
    enable: bool = True
    banned: bool = False
    force_join_channel: bool = True

    @validator("username")
    def validate_username(cls, username: str):
        if not username:
            raise ValueError("Username can not be null")

        return username


class UserCreate(UserBase):
    password: str
    referral_user_id: Optional[int]

    @property
    def hashed_password(self):
        return pwd_context.hash(self.password)

    @validator("password")
    def validate_password(cls, password: str):
        if not password:
            raise ValueError("Password can not be null")

        return password


class UserModify(UserBase):
    id: int


class UserResponse(UserBase):
    id: int
    balance: Optional[int] = 0
    balance_readable: Optional[str] = 0
    accounts: List["AccountResponse"] = {}
    created_at: datetime
    modified_at: datetime
    full_name: str

    def dict(cls, *args, **kwargs):
        return super().dict(*args, **kwargs)

    class Config:
        orm_mode = True


class UsersResponse(BaseModel):
    users: List[UserResponse]
    total: int
