from datetime import datetime
from enum import Enum
from typing import List

from pydantic import BaseModel, root_validator, validator


class HostType(str, Enum):
    # default = "X-UI-MHSANAEI"
    x_ui_sanaei = "X-UI-MHSANAEI"
    x_ui_kafka = "X-UI-FRANZKAFKAYU"


class HostZoneBase(BaseModel):
    name: str
    description: str
    max_account: int
    enable: bool


class HostZoneCreate(HostZoneBase):
    pass


class HostZoneModify(HostZoneBase):
    id: int


class HostZoneResponse(HostZoneBase):
    id: int
    created_at: datetime
    modified_at: datetime

    def dict(cls, *args, **kwargs):
        return super().dict(*args, **kwargs)

    class Config:
        orm_mode = True


class HostZonesResponse(BaseModel):
    host_zones: List[HostZoneResponse]
    total: int


class Host(BaseModel):
    host_zone_id: int
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
    host_zone: HostZoneResponse
    created_at: datetime
    modified_at: datetime

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
