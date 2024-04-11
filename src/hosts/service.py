import random
import string
from enum import Enum
from typing import Optional, List, Union, Tuple

from sqlalchemy import or_
from sqlalchemy.orm import Session

from src.hosts.models import Host, HostZone
from src.hosts.schemas import HostCreate, HostModify, HostZoneCreate, HostZoneModify
from src.inbounds.models import Inbound
from src.inbounds.schemas import InboundCreate
import src.inbounds.service as inbound_service

HostSortingOptions = Enum(
    "HostSortingOptions",
    {
        "created": Host.created_at.asc(),
        "-created": Host.created_at.desc(),
        "modified": Host.modified_at.asc(),
        "-modified": Host.modified_at.desc(),
        "domain": Host.domain.asc(),
        "-domain": Host.domain.desc(),
        "name": Host.name.asc(),
        "-name": Host.name.desc(),
        "ip": Host.ip.asc(),
        "-ip": Host.ip.desc(),
    },
)

HostZoneSortingOptions = Enum(
    "HostZoneSortingOptions",
    {
        "created": HostZone.created_at.asc(),
        "-created": HostZone.created_at.desc(),
        "modified": HostZone.modified_at.asc(),
        "-modified": HostZone.modified_at.desc(),
        "name": HostZone.name.asc(),
        "-name": HostZone.name.desc(),
    },
)


def create_host(db: Session, host: HostCreate, db_host_zone: HostZone = None):
    db_host = Host(
        name=host.name,
        host_zone_id=1 if db_host_zone is None else db_host_zone.id,
        domain=host.domain,
        port=host.port,
        ip=host.ip,
        username=host.username,
        password=host.password,
        api_path=host.api_path,
        enable=host.enable,
        master=host.master,
        type=host.type,
    )

    db.add(db_host)
    db.commit()
    db.refresh(db_host)
    return db_host


def update_host(db: Session, db_host: Host, modify: HostModify):
    db_host.name = modify.name
    db_host.host_zone_id = modify.host_zone_id
    db_host.domain = modify.domain
    db_host.username = modify.username
    db_host.password = modify.password
    db_host.ip = modify.ip
    db_host.port = modify.port
    db_host.api_path = modify.api_path
    db_host.master = modify.master
    db_host.enable = modify.enable
    db_host.type = modify.type

    db.commit()
    db.refresh(db_host)

    return db_host


def copy_host(db: Session, db_host: Host):

    ip = ".".join(map(str, (random.randint(0, 255) for _ in range(4))))

    domain_prefix = "".join(random.choice(string.ascii_lowercase) for _ in range(3))

    new_domain = domain_prefix + "." + db_host.domain

    new_db_host = Host(
        name=db_host.name + " Clone",
        host_zone_id=db_host.host_zone_id,
        domain=new_domain,
        port=db_host.port,
        ip=ip,
        username=db_host.username,
        password=db_host.password,
        api_path=db_host.api_path,
        enable=False,
        master=db_host.master,
        type=db_host.type,
    )

    db.add(new_db_host)
    db.commit()
    db.refresh(new_db_host)

    for db_inbound in db_host.inbounds:
        new_inbound = InboundCreate(
            remark=db_inbound.remark,
            host_id=new_db_host.id,
            port=db_inbound.port,
            domain=db_inbound.domain,
            request_host=db_inbound.request_host,
            sni=db_inbound.sni,
            address=db_inbound.address,
            path=db_inbound.path,
            key=db_inbound.key,
            enable=db_inbound.enable,
            develop=db_inbound.develop,
            security=db_inbound.security,
            flow=db_inbound.flow,
            type=db_inbound.type,
        )

        inbound_service.create_inbound(db=db, db_host=new_db_host, inbound=new_inbound)

    return new_db_host


def get_hosts(
    db: Session,
    offset: Optional[int] = None,
    limit: Optional[int] = None,
    sort: Optional[List[HostSortingOptions]] = None,
    q: str = None,
    enable: int = -1,
    return_with_count: bool = True,
) -> Tuple[List[Host], int]:
    query = db.query(Host)

    if enable >= 0:
        query = query.filter(Host.enable == (True if enable > 0 else False))

    if q:
        query = query.filter(
            or_(
                Host.name.ilike(f"%{q}%"),
                Host.domain.ilike(f"%{q}%"),
                Host.ip.ilike(f"%{q}%"),
                Host.port.ilike(f"%{q}%"),
            )
        )

    if sort:
        query = query.order_by(*(opt.value for opt in sort))

    count = query.count()

    if offset:
        query = query.offset(offset)
    if limit:
        query = query.limit(limit)

    if return_with_count:
        return query.all(), count
    else:
        return query.all()


def remove_host(db: Session, db_host: Host):
    db.delete(db_host)
    db.commit()
    return db_host


def get_host(db: Session, host_id: int):
    return db.query(Host).filter(Host.id == host_id).first()


# HostZone CRUDs


def create_host_zone(db: Session, host_zone: HostZoneCreate):
    db_host_zone = HostZone(
        name=host_zone.name,
        description=host_zone.description,
        max_account=host_zone.max_account,
        enable=host_zone.enable,
    )

    db.add(db_host_zone)
    db.commit()
    db.refresh(db_host_zone)
    return db_host_zone


def update_host_zone(db: Session, db_host_zone: HostZone, modify: HostZoneModify):
    db_host_zone.name = modify.name
    db_host_zone.description = modify.description
    db_host_zone.max_account = modify.max_account
    db_host_zone.enable = modify.enable

    db.commit()
    db.refresh(db_host_zone)

    return db_host_zone


def get_host_zones(
    db: Session,
    offset: Optional[int] = None,
    limit: Optional[int] = None,
    sort: Optional[List[HostZoneSortingOptions]] = None,
    q: str = None,
    enable: int = -1,
    return_with_count: bool = True,
) -> Tuple[List[HostZone], int]:
    query = db.query(HostZone)

    if enable >= 0:
        query = query.filter(HostZone.enable == (True if enable > 0 else False))

    if q:
        query = query.filter(
            or_(
                HostZone.name.ilike(f"%{q}%"),
                HostZone.description.ilike(f"%{q}%"),
            )
        )

    if sort:
        query = query.order_by(*(opt.value for opt in sort))

    count = query.count()

    if offset:
        query = query.offset(offset)
    if limit:
        query = query.limit(limit)

    if return_with_count:
        return query.all(), count
    else:
        return query.all()


def remove_host_zone(db: Session, db_host_zone: HostZone):
    db.delete(db_host_zone)
    db.commit()
    return db_host_zone


def get_host_zone(db: Session, host_zone_id: int) -> HostZone:
    return db.query(HostZone).filter(HostZone.id == host_zone_id).first()
