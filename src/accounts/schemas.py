from typing import List
from uuid import uuid4, UUID

from pydantic import BaseModel, validator, Field

from src.users.schemas import UserResponse


class AccountBase(BaseModel):
    user_id: int
    uuid: UUID = Field(default_factory=uuid4)
    email: str

    enable: bool


class AccountCreate(AccountBase):
    password: str

    @validator("uuid")
    def validate_uuid(cls, uuid: str):
        if not uuid:
            raise ValueError("UUID can not be null")

        return uuid

    @validator("password")
    def validate_email(cls, email: str):
        if not email:
            raise ValueError("Email can not be null")

        return email


class AccountModify(AccountBase):
    id: int


class AccountResponse(AccountBase):
    id: int

    user: UserResponse

    def dict(cls, *args, **kwargs):
        return super().dict(*args, **kwargs)

    class Config:
        orm_mode = True


class AccountsResponse(BaseModel):
    users: List[AccountResponse]
    total: int
