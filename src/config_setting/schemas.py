# Pydantic models for API
from datetime import datetime
from typing import Optional, Any, Dict

from pydantic import BaseModel


class ConfigSettingCreate(BaseModel):
    key: str
    value: Any
    description: Optional[str] = None


class ConfigSettingsBulkUpdate(BaseModel):
    settings: Dict[str, Any]


class ConfigSettingResponse(BaseModel):
    key: str
    value: Any
    value_type: str
    updated_at: datetime

    class Config:
        orm_mode = True
