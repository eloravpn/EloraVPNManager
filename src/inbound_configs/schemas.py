from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, validator

from src.inbounds.schemas import (
    InboundSecurity,
    InboundType,
    InboundFingerPrint,
    InboundResponse,
    InboundNetwork,
)


class InboundConfigBase(BaseModel):
    remark: str
    inbound_id: int
    port: int
    domain: str
    host: str
    sni: str
    address: str
    path: str
    pbk: Optional[str]
    sid: Optional[str]
    spx: Optional[str]
    alpns: Optional[List[str]] = None
    enable: bool
    develop: bool
    network: InboundNetwork = InboundNetwork.ws
    finger_print: InboundFingerPrint = InboundFingerPrint.default
    security: InboundSecurity = InboundSecurity.default
    type: InboundType = InboundType.default


class InboundConfigCreate(InboundConfigBase):
    @validator("remark")
    def validate_remark(cls, remark: str):
        if not remark:
            raise ValueError("Remark can not be null")

        return remark


class InboundConfigModify(InboundConfigBase):
    id: int


class InboundConfigResponse(InboundConfigBase):
    id: int
    inbound: InboundResponse
    created_at: datetime
    modified_at: datetime

    def dict(cls, *args, **kwargs):
        return super().dict(*args, **kwargs)

    class Config:
        orm_mode = True


class InboundConfigsResponse(BaseModel):
    inbound_configs: List[InboundConfigResponse]
    total: int
