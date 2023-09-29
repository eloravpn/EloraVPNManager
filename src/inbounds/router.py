from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

import src.inbounds.service as service
import src.hosts.service as host_service
from src.admins.schemas import Admin
from src.database import get_db
from src.inbounds.schemas import (
    InboundCreate,
    InboundsResponse,
    InboundModify,
    InboundResponse,
)

router = APIRouter()


@router.post("/inbounds/", response_model=InboundResponse)
def add_inbound(
    inbound: InboundCreate,
    db: Session = Depends(get_db),
    admin: Admin = Depends(Admin.get_current),
):
    db_host = host_service.get_host(db, inbound.host_id)
    if not db_host:
        raise HTTPException(status_code=404, detail="Host not found")

    try:
        db_inbound = service.create_inbound(db=db, db_host=db_host, inbound=inbound)
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Inbound already exists")

    return db_inbound


@router.put("/inbounds/{inbound_id}", tags=["Inbound"], response_model=InboundResponse)
def modify_inbound(
    inbound_id: int,
    inbound: InboundModify,
    db: Session = Depends(get_db),
    admin: Admin = Depends(Admin.get_current),
):
    db_inbound = service.get_inbound(db, inbound_id)
    if not db_inbound:
        raise HTTPException(status_code=404, detail="Inbound not found")

    return service.update_inbound(db=db, db_inbound=db_inbound, modify=inbound)


@router.get("/inbounds/{inbound_id}", tags=["Inbound"], response_model=InboundResponse)
def get_inbound(
    inbound_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(Admin.get_current),
):
    db_inbound = service.get_inbound(db, inbound_id)
    if not db_inbound:
        raise HTTPException(status_code=404, detail="Inbound not found")

    return db_inbound


@router.delete("/inbounds/{inbound_id}", tags=["Inbound"])
def delete_inbound(
    inbound_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(Admin.get_current),
):
    db_inbound = service.get_inbound(db, inbound_id)
    if not db_inbound:
        raise HTTPException(status_code=404, detail="Inbound not found")

    service.remove_inbound(db=db, db_inbound=db_inbound)
    return {}


@router.get("/inbounds/", tags=["Inbound"], response_model=InboundsResponse)
def get_inbounds(
    offset: int = None,
    limit: int = None,
    sort: str = None,
    enable: int = -1,
    host_id: int = 0,
    q: str = None,
    db: Session = Depends(get_db),
    admin: Admin = Depends(Admin.get_current),
):
    if sort is not None:
        opts = sort.strip(",").split(",")
        sort = []
        for opt in opts:
            try:
                sort.append(service.InboundSortingOptions[opt])
            except KeyError:
                raise HTTPException(
                    status_code=400, detail=f'"{opt}" is not a valid sort option'
                )

    inbounds, count = service.get_inbounds(
        db=db,
        offset=offset,
        limit=limit,
        enable=enable,
        q=q,
        sort=sort,
        host_id=host_id,
    )

    return {"inbounds": inbounds, "total": count}
