from datetime import datetime
from typing import List, Optional, Union, TYPE_CHECKING
from uuid import uuid4, UUID

from pydantic import BaseModel, validator, Field


class AccountBase(BaseModel):
    user_id: int
    # TODO: due to a circular import
    # user: Optional["UserResponse"]
    uuid: str = Field(default_factory=uuid4)
    data_limit: int
    email: str
    enable: bool
    expired_at: Union[datetime, str] = None

    @validator("uuid")
    def validate_uuid(cls, uuid: str):
        if not uuid:
            raise ValueError("UUID can not be null")
        # else:
        #     UUID(uuid, version=4)

        return uuid

    @validator("email")
    def validate_email(cls, email: str):
        if not email:
            raise ValueError("Email can not be null")

        return email


class AccountCreate(AccountBase):
    user_id: int


class AccountModify(AccountBase):
    id: int


# from src.users.schemas import UserResponse
class AccountResponse(AccountBase):
    id: int
    used_traffic: int
    created_at: datetime
    modified_at: datetime

    def dict(cls, *args, **kwargs):
        return super().dict(*args, **kwargs)

    class Config:
        orm_mode = True


class AccountsResponse(BaseModel):
    accounts: List[AccountResponse]
    total: int
