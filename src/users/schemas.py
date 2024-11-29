import secrets
import string
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
    password: Optional[str] = None
    referral_user_id: Optional[int]

    @property
    def hashed_password(self):
        return pwd_context.hash(self.password)

    @classmethod
    def generate_password(cls, length: int = 12) -> str:
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        return "".join(secrets.choice(chars) for _ in range(length))

    @validator("password")
    def validate_password(cls, password: str = None):
        print(password)
        if password is None:
            return cls.generate_password()
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
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
