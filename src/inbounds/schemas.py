from enum import Enum
from typing import List

from pydantic import BaseModel, validator, root_validator


class InboundType(str, Enum):
    # inbound_type = protocol

    VMess = "vmess"
    VLESS = "vless"
    Trojan = "trojan"
    Shadowsocks = "shadowsocks"


class InboundSecurity(str, Enum):
    inbound_default = "tls"
    none = "none"
    tls = "tls"


class InboundBase(BaseModel):
    remark: str
    host_id: int
    port: int
    domain: str
    request_host: str
    sni: str
    address: str
    path: str
    enable: bool
    develop: bool
    security: InboundSecurity = InboundSecurity.tls
    type: InboundType = InboundType.VLESS


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

    def dict(cls, *args, **kwargs):
        return super().dict(*args, **kwargs)

    class Config:
        orm_mode = True


class InboundsResponse(BaseModel):
    inbounds: List[InboundResponse]
    total: int
