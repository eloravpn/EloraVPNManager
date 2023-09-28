from typing import List, Tuple

from sqlalchemy.orm import Session

from src.hosts.models import Host
from src.inbounds.models import Inbound
from src.inbounds.schemas import InboundCreate, InboundModify


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


def get_inbounds(db: Session) -> Tuple[List[Inbound], int]:
    query = db.query(Inbound)

    count = query.count()

    return query.all(), count


def remove_inbound(db: Session, db_inbound: Inbound):
    db.delete(db_inbound)
    db.commit()
    return db_inbound


def get_inbound(db: Session, inbound_id: int):
    return db.query(Inbound).filter(Inbound.id == inbound_id).first()
