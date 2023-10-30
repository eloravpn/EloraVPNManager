from datetime import datetime
from enum import Enum, StrEnum
from typing import List, Optional

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
    reality = "reality"


class InboundNetwork(str, Enum):
    ws = "ws"
    tcp = "tcp"
    grpc = "grpc"


class InboundFingerPrint(str, Enum):
    default = "none"

    none = "none"
    chrome = "chrome"
    firefox = "firefox"


class InboundFlow(StrEnum):
    xtls_rprx_vision = "xtls-rprx-vision"
    xtls_rprx_vision_udp443 = "xtls-rprx-vision-udp443"


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
    flow: Optional[InboundFlow]


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
