from datetime import datetime
from enum import Enum
from typing import List

from pydantic import BaseModel, validator, root_validator

from src.hosts.schemas import HostResponse


class InboundType(str, Enum):
    default = "vless"

    VMess = "vmess"
    VLESS = "vless"
    Trojan = "trojan"
    Shadowsocks = "shadowsocks"


class InboundSecurity(str, Enum):
    default = "tls"

    none = "none"
    tls = "tls"


class InboundNetwork(str, Enum):
    ws = "ws"
    tcp = "tcp"


class InboundFingerPrint(str, Enum):
    default = "none"

    none = "none"
    chrome = "chrome"
    firefox = "firefox"


class InboundBase(BaseModel):
    remark: str
    host_id: int
    key: int
    port: int
    domain: str
    request_host: str
    sni: str
    address: str
    path: str
    enable: bool
    develop: bool
    security: InboundSecurity = InboundSecurity.default
    type: InboundType = InboundType.default


class InboundCreate(InboundBase):
    @validator("remark")
    def validate_remark(cls, remark: str):
        if not remark:
            raise ValueError("Remark can not be null")

        return remark


class InboundModify(InboundBase):
    id: int


class InboundResponse(InboundBase):
    id: int
    host: HostResponse
    created_at: datetime
    modified_at: datetime

    def dict(cls, *args, **kwargs):
        return super().dict(*args, **kwargs)

    class Config:
        orm_mode = True


class InboundsResponse(BaseModel):
    inbounds: List[InboundResponse]
    total: int
