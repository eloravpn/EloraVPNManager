from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List

from .schemas import (
    ConfigSettingCreate,
    ConfigSettingResponse,
    ConfigSettingsBulkUpdate,
)
from .service import get_all_setting, get_setting, set_setting, delete_setting
from .. import Admin
from ..database import get_db

router = APIRouter()


@router.get("/settings", response_model=List[ConfigSettingResponse])
async def list_configs(
    db: Session = Depends(get_db), admin: Admin = Depends(Admin.get_current)
):
    """List all configurations"""
    return get_all_setting(db)


@router.get("/settings/{key}", response_model=ConfigSettingResponse)
async def get_config(
    key: str, db: Session = Depends(get_db), admin: Admin = Depends(Admin.get_current)
):
    """Get specific configuration"""
    setting = get_setting(db, key)
    if not setting:
        raise HTTPException(status_code=404, detail="Configuration not found")
    return setting


@router.post("/settings")
async def update_config(
    config: ConfigSettingCreate,
    db: Session = Depends(get_db),
    admin: Admin = Depends(Admin.get_current),
):
    """Update or create configuration"""
    set_setting(db, config.key, config.value)
    return {"status": "success", "message": "Configuration Added"}


@router.put("/settings/{key}")
async def update_config(
    config: ConfigSettingCreate,
    db: Session = Depends(get_db),
    admin: Admin = Depends(Admin.get_current),
):
    """Update or create configuration"""
    set_setting(db, config.key, config.value)
    return {"status": "success", "message": "Configuration Added"}


@router.post("/settings/bulk")
async def update_bulk_config(
    configs: ConfigSettingsBulkUpdate,
    db: Session = Depends(get_db),
    admin: Admin = Depends(Admin.get_current),
):
    """Update or create configuration"""
    for key, value in configs.settings.items():
        set_setting(db, key, value)
    return {"status": "success", "message": "Configurations updated"}


@router.delete("/settings/{key}")
async def delete_config(
    key: str, db: Session = Depends(get_db), admin: Admin = Depends(Admin.get_current)
):
    """Delete configuration"""
    if not delete_setting(db, key):
        raise HTTPException(status_code=404, detail="Configuration not found")
    return {"status": "success", "message": "Configuration deleted"}
