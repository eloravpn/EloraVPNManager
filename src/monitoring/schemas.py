from datetime import datetime

from pydantic import BaseModel, validator


class MonitoringResultBase(BaseModel):
    client_name: str
    client_ip: str
    test_url: str
    remark: str
    port: int
    domain: str
    sni: str
    delay: int
    ping: int
    develop: bool
    success: bool


class MonitoringResultResponse(MonitoringResultBase):
    id: int
    created_at: datetime
    modified_at: datetime

    def dict(cls, *args, **kwargs):
        return super().dict(*args, **kwargs)

    class Config:
        orm_mode = True


class MonitoringResultCreate(MonitoringResultBase):
    pass
