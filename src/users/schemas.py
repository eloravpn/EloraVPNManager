import re
from typing import List

from passlib.context import CryptContext
from pydantic import BaseModel, validator

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

USERNAME_REGEXP = re.compile(r'^(?=\w{3,32}\b)[a-zA-Z0-9]+(?:_[a-zA-Z0-9]+)*$')


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


class UserCreate(UserBase):
    password: str


    @property
    def hashed_password(self):
        return pwd_context.hash(self.password)

    @validator("username")
    def validate_username(cls, username: str):
        if not username:
            raise ValueError("Username can not be null")
        elif not USERNAME_REGEXP.match(username):
            raise ValueError(
                'Username only can be 3 to 32 characters and contain a-z, 0-9, and underscores in between.')

        return username

    @validator("password")
    def validate_password(cls, password: str):
        if not password:
            raise ValueError("Password can not be null")

        return password


class UserModify(UserBase):
    id: int


class UserResponse(UserBase):
    id: int

    def dict(cls, *args, **kwargs):
        return super().dict(*args, **kwargs)

    class Config:
        orm_mode = True


class UsersResponse(BaseModel):
    users: List[UserResponse]
    total: int
