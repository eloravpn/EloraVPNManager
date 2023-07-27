from enum import Enum
from typing import Optional, List, Union, Tuple

from sqlalchemy.orm import Session

from src.hosts.models import Host
from src.hosts.schemas import HostCreate, HostModify

HostSortingOptions = Enum('HostSortingOptions', {
    'domain': Host.domain.asc(),
    '-domain': Host.domain.desc()
})


def create_host(db: Session, host: HostCreate):
    db_host = Host(name=host.name, domain=host.domain, port=host.port, ip=host.ip,
                   username=host.username, password=host.password, api_path=host.api_path,
                   enable=host.enable, master=host.master, type=host.type)

    db.add(db_host)
    db.commit()
    db.refresh(db_host)
    return db_host


def update_host(db: Session, db_host: Host, modify: HostModify):

    db_host.name = modify.name
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


def get_hosts(db: Session,
              offset: Optional[int] = None,
              limit: Optional[int] = None,
              sort: Optional[List[HostSortingOptions]] = None
              ) -> Tuple[List[Host], int]:
    query = db.query(Host)

    if sort:
        query = query.order_by(*(opt.value for opt in sort))

    if offset:
        query = query.offset(offset)
    if limit:
        query = query.limit(limit)

    count = query.count()

    return query.all(), count


def remove_host(db: Session, db_host: Host):
    db.delete(db_host)
    db.commit()
    return db_host


def get_host(db: Session, host_id: int):
    return db.query(Host).filter(Host.id == host_id).first()
