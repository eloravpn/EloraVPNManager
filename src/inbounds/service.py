from enum import Enum
from typing import List, Tuple, Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session

from src.hosts.models import Host
from src.inbounds.models import Inbound
from src.inbounds.schemas import InboundCreate, InboundModify

InboundSortingOptions = Enum(
    "InboundSortingOptions",
    {
        "created": Inbound.created_at.asc(),
        "-created": Inbound.created_at.desc(),
        "modified": Inbound.modified_at.asc(),
        "-modified": Inbound.modified_at.desc(),
        "remark": Inbound.remark.asc(),
        "-remark": Inbound.remark.desc(),
        "address": Inbound.address.asc(),
        "-address": Inbound.address.desc(),
        "sni": Inbound.sni.asc(),
        "-sni": Inbound.sni.desc(),
        "request_host": Inbound.request_host.asc(),
        "-request_host": Inbound.request_host.desc(),
    },
)


def create_inbound(db: Session, db_host: Host, inbound: InboundCreate):
    db_inbound = Inbound(
        remark=inbound.remark,
        host_id=db_host.id,
        port=inbound.port,
        domain=inbound.domain,
        request_host=inbound.request_host,
        sni=inbound.sni,
        address=inbound.address,
        path=inbound.path,
        key=inbound.key,
        enable=inbound.enable,
        develop=inbound.develop,
        security=inbound.security,
        type=inbound.type,
    )

    db.add(db_inbound)
    db.commit()
    db.refresh(db_inbound)
    return db_inbound


def update_inbound(db: Session, db_inbound: Inbound, modify: InboundModify):
    db_inbound.host_id = modify.host_id
    db_inbound.remark = modify.remark
    db_inbound.key = modify.key
    db_inbound.port = modify.port
    db_inbound.request_host = modify.request_host
    db_inbound.sni = modify.sni
    db_inbound.address = modify.address
    db_inbound.path = modify.path
    db_inbound.enable = modify.enable
    db_inbound.develop = modify.develop
    db_inbound.security = modify.security
    db_inbound.type = modify.type

    db.commit()
    db.refresh(db_inbound)

    return db_inbound


def get_inbounds(
    db: Session,
    offset: Optional[int] = None,
    limit: Optional[int] = None,
    sort: Optional[List[InboundSortingOptions]] = [InboundSortingOptions["remark"]],
    q: str = None,
    enable: int = -1,
    host_id: int = 0,
    return_with_count: bool = True,
) -> Tuple[List[Inbound], int]:
    query = db.query(Inbound)

    if enable >= 0:
        query = query.filter(Inbound.enable == (True if enable > 0 else False))

    if host_id > 0:
        query = query.filter(Inbound.host_id == host_id)

    if q:
        query = query.filter(
            or_(
                Inbound.remark.ilike(f"%{q}%"),
                Inbound.domain.ilike(f"%{q}%"),
                Inbound.address.ilike(f"%{q}%"),
                Inbound.sni.ilike(f"%{q}%"),
                Inbound.request_host.ilike(f"%{q}%"),
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


def remove_inbound(db: Session, db_inbound: Inbound):
    db.delete(db_inbound)
    db.commit()
    return db_inbound


def get_inbound(db: Session, inbound_id: int):
    return db.query(Inbound).filter(Inbound.id == inbound_id).first()
