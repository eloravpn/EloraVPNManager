from enum import Enum
from typing import List

from pydantic import BaseModel, root_validator, validator


class HostType(str, Enum):
    # default = "X-UI-MHSANAEI"
    x_ui_sanaei = "X-UI-MHSANAEI"
    x_ui_kafka = "X-UI-FRANZKAFKAYU"


class Host(BaseModel):
    name: str
    domain: str
    port: int
    username: str
    password: str
    ip: str
    api_path: str
    enable: bool
    master: bool
    type: HostType = HostType.x_ui_sanaei


class HostResponse(Host):
    id: int

    def dict(cls, *args, **kwargs):
        return super().dict(*args, **kwargs)

    class Config:
        orm_mode = True


class HostCreate(Host):

    @validator("name")
    def validate_name(cls, name: str):
        if not name:
            raise ValueError("Name can not be null")

        return name


class HostModify(Host):
    id: int

    @validator("name")
    def validate_name(cls, name: str):
        if not name:
            raise ValueError("Name can not be null")

        return name


class HostsResponse(BaseModel):
    hosts: List[HostResponse]
    total: int
