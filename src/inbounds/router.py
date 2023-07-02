from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

import src.inbounds.service as service
import src.hosts.service as host_service
from src.admins.schemas import Admin
from src.database import get_db
from src.inbounds.schemas import InboundCreate, InboundsResponse, InboundModify, InboundResponse

router = APIRouter()


@router.post("/inbounds/", response_model=InboundResponse)
def add_inbound(inbound: InboundCreate,
                db: Session = Depends(get_db),
                admin: Admin = Depends(Admin.get_current)):
    db_host = host_service.get_host(db, inbound.host_id)
    if not db_host:
        raise HTTPException(status_code=404, detail="Host not found")

    try:
        db_inbound = service.create_inbound(db=db, db_host=db_host, inbound=inbound)
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Inbound already exists")

    return db_inbound


@router.put("/inbounds/{inbound_id}", tags=["Inbound"], response_model=InboundResponse)
def modify_inbound(inbound_id: int, inbound: InboundModify,
                   db: Session = Depends(get_db),
                   admin: Admin = Depends(Admin.get_current)):
    db_inbound = service.get_inbound(db, inbound_id)
    if not db_inbound:
        raise HTTPException(status_code=404, detail="Inbound not found")

    return service.update_inbound(db=db, db_inbound=db_inbound, modify=inbound)


@router.get("/inbounds/{inbound_id}", tags=["Inbound"],
            response_model=InboundResponse)
def get_inbound(inbound_id: int, db: Session = Depends(get_db),
                admin: Admin = Depends(Admin.get_current)):
    db_inbound = service.get_inbound(db, inbound_id)
    if not db_inbound:
        raise HTTPException(status_code=404, detail="Inbound not found")

    return db_inbound


@router.delete("/inbounds/{inbound_id}", tags=["Inbound"])
def get_inbound(inbound_id: int, db: Session = Depends(get_db),
                admin: Admin = Depends(Admin.get_current)):
    db_inbound = service.get_inbound(db, inbound_id)
    if not db_inbound:
        raise HTTPException(status_code=404, detail="Inbound not found")

    service.remove_inbound(db=db, db_inbound=db_inbound)
    return {}


@router.get("/inbounds/", tags=['Inbound'], response_model=InboundsResponse)
def get_inbounds(
        db: Session = Depends(get_db),
        admin: Admin = Depends(Admin.get_current)
):
    inbounds, count = service.get_inbounds(db=db)

    return {"inbounds": inbounds, "total": count}
