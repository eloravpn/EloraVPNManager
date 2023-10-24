from typing import List

from apscheduler.jobstores import sqlalchemy
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.admins.schemas import Admin
from src.database import get_db, Base, engine
from src.hosts.schemas import (
    HostCreate,
    HostResponse,
    HostsResponse,
    HostModify,
    HostZonesResponse,
)
import src.hosts.service as service

router = APIRouter()


@router.post("/hosts/", response_model=HostResponse)
def add_host(
    host: HostCreate,
    db: Session = Depends(get_db),
    admin: Admin = Depends(Admin.get_current),
):
    db_host_zone = service.get_host_zone(db, host.host_zone_id)
    if not db_host_zone:
        raise HTTPException(
            status_code=404,
            detail="Hose Zone not found with id " + host.host_zone_id,
        )

    try:
        db_host = service.create_host(db=db, db_host_zone=db_host_zone, host=host)
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Host already exists")

    return db_host


@router.put("/hosts/{host_id}", tags=["Host"], response_model=HostResponse)
def modify_host(
    host_id: int,
    host: HostModify,
    db: Session = Depends(get_db),
    admin: Admin = Depends(Admin.get_current),
):
    db_host = service.get_host(db, host_id)
    if not db_host:
        raise HTTPException(status_code=404, detail="Host not found")

    return service.update_host(db=db, db_host=db_host, modify=host)


@router.get("/hosts/{host_id}", tags=["Host"], response_model=HostResponse)
def get_host(
    host_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(Admin.get_current),
):
    db_host = service.get_host(db, host_id)
    if not db_host:
        raise HTTPException(status_code=404, detail="Host not found")

    return db_host


@router.delete("/hosts/{host_id}", tags=["Host"])
def get_host(
    host_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(Admin.get_current),
):
    db_host = service.get_host(db, host_id)
    if not db_host:
        raise HTTPException(status_code=404, detail="Host not found")

    service.remove_host(db=db, db_host=db_host)
    return {}


@router.get("/hosts/", tags=["Host"], response_model=HostsResponse)
def get_hosts(
    offset: int = None,
    limit: int = None,
    sort: str = None,
    enable: int = -1,
    q: str = None,
    db: Session = Depends(get_db),
    admin: Admin = Depends(Admin.get_current),
):
    if sort is not None:
        opts = sort.strip(",").split(",")
        sort = []
        for opt in opts:
            try:
                sort.append(service.HostSortingOptions[opt])
            except KeyError:
                raise HTTPException(
                    status_code=400, detail=f'"{opt}" is not a valid sort option'
                )

    hosts, count = service.get_hosts(
        db=db, offset=offset, limit=limit, enable=enable, q=q, sort=sort
    )

    return {"hosts": hosts, "total": count}


@router.get("/host-zones/", tags=["HostZone"], response_model=HostZonesResponse)
def get_host_zones(
    offset: int = None,
    limit: int = None,
    sort: str = None,
    enable: int = -1,
    q: str = None,
    db: Session = Depends(get_db),
    admin: Admin = Depends(Admin.get_current),
):
    if sort is not None:
        opts = sort.strip(",").split(",")
        sort = []
        for opt in opts:
            try:
                sort.append(service.HostZoneSortingOptions[opt])
            except KeyError:
                raise HTTPException(
                    status_code=400, detail=f'"{opt}" is not a valid sort option'
                )

    host_zones, count = service.get_host_zones(
        db=db, offset=offset, limit=limit, enable=enable, q=q, sort=sort
    )

    return {"host_zones": host_zones, "total": count}
