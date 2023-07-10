
from typing import List

from passlib.context import CryptContext
from pydantic import BaseModel, validator

from src.accounts.schemas import AccountResponse

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserBase(BaseModel):
    username: str
    first_name: str
    last_name: str
    description: str
    telegram_chat_id: int
    telegram_username: str
    phone_number: str
    enable: bool
    banned: bool

    @validator("username")
    def validate_username(cls, username: str):
        if not username:
            raise ValueError("Username can not be null")

        return username


class UserCreate(UserBase):
    password: str

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
    accounts: List[AccountResponse] = {}

    def dict(cls, *args, **kwargs):
        return super().dict(*args, **kwargs)

    class Config:
        orm_mode = True


class UsersResponse(BaseModel):
    users: List[UserResponse]
    total: int
