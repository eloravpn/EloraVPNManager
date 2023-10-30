from enum import Enum
from typing import List, Tuple, Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session

from src.hosts.models import HostZone, Host
from src.inbound_configs.models import InboundConfig
from src.inbound_configs.schemas import InboundConfigCreate, InboundConfigModify
from src.inbounds.models import Inbound

InboundConfigSortingOptions = Enum(
    "InboundConfigSortingOptions",
    {
        "created": InboundConfig.created_at.asc(),
        "-created": InboundConfig.created_at.desc(),
        "modified": InboundConfig.modified_at.asc(),
        "-modified": InboundConfig.modified_at.desc(),
        "remark": InboundConfig.remark.asc(),
        "-remark": InboundConfig.remark.desc(),
        "address": InboundConfig.address.asc(),
        "-address": InboundConfig.address.desc(),
        "sni": InboundConfig.sni.asc(),
        "-sni": InboundConfig.sni.desc(),
        "host": InboundConfig.host.asc(),
        "-host": InboundConfig.host.desc(),
    },
)


def create_inbound_config(
    db: Session, db_inbound: Inbound, inbound_config: InboundConfigCreate
):
    db_inbound_config = InboundConfig(
        remark=inbound_config.remark,
        inbound_id=db_inbound.id,
        port=inbound_config.port,
        domain=inbound_config.domain,
        host=inbound_config.host,
        sni=inbound_config.sni,
        finger_print=inbound_config.finger_print,
        address=inbound_config.address,
        path=inbound_config.path,
        spx=db_inbound_config.spx,
        sid=db_inbound_config.sid,
        pbk=db_inbound_config.pbk,
        enable=inbound_config.enable,
        develop=inbound_config.develop,
        security=inbound_config.security,
        network=inbound_config.network,
        type=inbound_config.type,
    )

    db.add(db_inbound_config)
    db.commit()
    db.refresh(db_inbound_config)
    return db_inbound_config


def copy_inbound_config(db: Session, db_inbound_config: InboundConfig):
    new_db_inbound_config = InboundConfig(
        remark=db_inbound_config.remark + " Clone",
        inbound_id=db_inbound_config.inbound_id,
        port=db_inbound_config.port,
        domain=db_inbound_config.domain,
        host=db_inbound_config.host,
        sni=db_inbound_config.sni,
        finger_print=db_inbound_config.finger_print,
        address=db_inbound_config.address,
        path=db_inbound_config.path,
        spx=db_inbound_config.spx,
        sid=db_inbound_config.sid,
        pbk=db_inbound_config.pbk,
        enable=db_inbound_config.enable,
        develop=True,
        security=db_inbound_config.security,
        network=db_inbound_config.network,
        type=db_inbound_config.type,
    )
    db.add(new_db_inbound_config)
    db.commit()
    db.refresh(new_db_inbound_config)
    return new_db_inbound_config


def update_inbound_config(
    db: Session, db_inbound_config: InboundConfig, modify: InboundConfigModify
):
    db_inbound_config.inbound_id = modify.inbound_id
    db_inbound_config.remark = modify.remark
    db_inbound_config.port = modify.port
    db_inbound_config.host = modify.host
    db_inbound_config.domain = modify.domain
    db_inbound_config.sni = modify.sni
    db_inbound_config.address = modify.address
    db_inbound_config.path = modify.path
    db_inbound_config.sid = modify.sid
    db_inbound_config.pbk = modify.pbk
    db_inbound_config.spx = modify.spx
    db_inbound_config.finger_print = modify.finger_print
    db_inbound_config.enable = modify.enable
    db_inbound_config.develop = modify.develop
    db_inbound_config.security = modify.security
    db_inbound_config.type = modify.type
    db_inbound_config.network = modify.network

    db.commit()
    db.refresh(db_inbound_config)

    return db_inbound_config


def get_inbound_configs(
    db: Session,
    offset: Optional[int] = None,
    limit: Optional[int] = None,
    sort: Optional[List[InboundConfigSortingOptions]] = [
        InboundConfigSortingOptions["remark"]
    ],
    q: str = None,
    enable: int = -1,
    inbound_id: int = 0,
    host_zone_id: int = 0,
    return_with_count: bool = True,
) -> Tuple[List[InboundConfig], int]:
    query = db.query(InboundConfig)

    if enable >= 0:
        query = query.filter(InboundConfig.enable == (True if enable > 0 else False))

    if inbound_id > 0:
        query = query.filter(InboundConfig.inbound_id == inbound_id)

    if q:
        query = query.filter(
            or_(
                InboundConfig.remark.ilike(f"%{q}%"),
                InboundConfig.domain.ilike(f"%{q}%"),
                InboundConfig.address.ilike(f"%{q}%"),
                InboundConfig.host.ilike(f"%{q}%"),
                InboundConfig.sni.ilike(f"%{q}%"),
            )
        )

    if host_zone_id > 0:
        query = query.join(Inbound, Inbound.id == InboundConfig.inbound_id)
        query = query.join(Host, Host.id == Inbound.host_id)
        query = query.join(HostZone, HostZone.id == Host.host_zone_id)
        query = query.filter(HostZone.id == host_zone_id)

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


def remove_inbound_config(db: Session, db_inbound_config: InboundConfig):
    db.delete(db_inbound_config)
    db.commit()
    return db_inbound_config


def get_inbound_config(db: Session, inbound_config_id: int):
    return db.query(InboundConfig).filter(InboundConfig.id == inbound_config_id).first()
