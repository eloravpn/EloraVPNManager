from datetime import datetime
from typing import List, Union
from uuid import uuid4

from pydantic import BaseModel, validator, Field


class AccountUsedTrafficResponse(BaseModel):
    account_id: int
    download: Union[int, None] = 0
    upload: Union[int, None] = 0


class AccountBase(BaseModel):
    user_id: int
    # TODO: due to a circular import
    # user: Optional["UserResponse"]
    uuid: str = Field(default_factory=lambda: str(uuid4()))
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
    used_traffic_percent: float
    created_at: datetime
    modified_at: datetime

    @validator('used_traffic_percent')
    def used_traffic_percent_check(cls, v):
        return round(v, 2)

    def dict(cls, *args, **kwargs):
        return super().dict(*args, **kwargs)

    class Config:
        orm_mode = True


class AccountsResponse(BaseModel):
    accounts: List[AccountResponse]
    total: int
