from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

import src.inbound_configs.service as service
import src.inbounds.service as inbound_service
from src.admins.schemas import Admin
from src.database import get_db
from src.inbound_configs.schemas import InboundConfigCreate, InboundConfigsResponse, InboundConfigModify, \
    InboundConfigResponse

router = APIRouter()


@router.post("/inbound-configs/", response_model=InboundConfigResponse)
def add_inbound_config(inbound_config: InboundConfigCreate,
                       db: Session = Depends(get_db),
                       admin: Admin = Depends(Admin.get_current)):
    db_inbound = inbound_service.get_inbound(db, inbound_config.inbound_id)
    if not db_inbound:
        raise HTTPException(status_code=404, detail="Inbound not found with id " +
                                                    inbound_config.inbound_id)

    try:
        db_inbound = service.create_inbound_config(db=db, db_inbound=db_inbound,
                                                   inbound_config=inbound_config)
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Inbound Config already exists")

    return db_inbound


@router.put("/inbound-configs/{inbound_config_id}", tags=["InboundConfig"], response_model=InboundConfigResponse)
def modify_inbound_config(inbound_config_id: int, inbound_config: InboundConfigModify,
                          db: Session = Depends(get_db),
                          admin: Admin = Depends(Admin.get_current)):
    db_inbound_config = service.get_inbound_config(db, inbound_config_id)
    if not db_inbound_config:
        raise HTTPException(status_code=404, detail="Inbound Config not found")

    return service.update_inbound_config(db=db, db_inbound_config=db_inbound_config, modify=inbound_config)


@router.get("/inbound-configs/{inbound_confi_id}", tags=["InboundConfig"],
            response_model=InboundConfigResponse)
def get_inbound_config(inbound_config_id: int, db: Session = Depends(get_db),
                admin: Admin = Depends(Admin.get_current)):
    db_inbound_config = service.get_inbound_config(db, inbound_config_id)
    if not db_inbound_config:
        raise HTTPException(status_code=404, detail="Inbound Config not found")

    return db_inbound_config


@router.delete("/inbound-configs/{inbound_config_id}", tags=["InboundConfig"])
def delete_inbound(inbound_config_id: int, db: Session = Depends(get_db),
                admin: Admin = Depends(Admin.get_current)):
    db_inbound_config = service.get_inbound_config(db, inbound_config_id)
    if not db_inbound_config:
        raise HTTPException(status_code=404, detail="Inbound Config not found")

    service.remove_inbound_config(db=db, db_inbound_config=db_inbound_config)
    return {}


@router.get("/inbound-configs/", tags=['InboundConfig'], response_model=InboundConfigsResponse)
def get_inbound_configs(
        db: Session = Depends(get_db),
        admin: Admin = Depends(Admin.get_current)
):
    inbound_configs, count = service.get_inbound_configs(db=db)

    return {"inbound_configs": inbound_configs, "total": count}
