from typing import List, Tuple

from sqlalchemy.orm import Session

from src.inbound_configs.models import InboundConfig
from src.inbound_configs.schemas import InboundConfigCreate, InboundConfigModify
from src.inbounds.models import Inbound


def create_inbound_config(db: Session, db_inbound: Inbound, inbound_config: InboundConfigCreate):
    db_inbound_config = InboundConfig(remark=inbound_config.remark, inbound_id=db_inbound.id, port=inbound_config.port,
                                      domain=inbound_config.domain, host=inbound_config.host,
                                      sni=inbound_config.sni, finger_print=inbound_config.finger_print,
                                      address=inbound_config.address, path=inbound_config.path,
                                      enable=inbound_config.enable, develop=inbound_config.develop,
                                      security=inbound_config.security,
                                      type=inbound_config.type)

    db.add(db_inbound_config)
    db.commit()
    db.refresh(db_inbound_config)
    return db_inbound_config


def copy_inbound_config(db: Session, db_inbound_config: InboundConfig):
    new_db_inbound_config = InboundConfig(remark=db_inbound_config.remark + " Clone",
                                          inbound_id=db_inbound_config.inbound_id,
                                          port=db_inbound_config.port, domain=db_inbound_config.domain,
                                          host=db_inbound_config.host, sni=db_inbound_config.sni,
                                          finger_print=db_inbound_config.finger_print,
                                          address=db_inbound_config.address, path=db_inbound_config.path,
                                          enable=db_inbound_config.enable, develop=True,
                                          security=db_inbound_config.security,
                                          type=db_inbound_config.type)
    db.add(new_db_inbound_config)
    db.commit()
    db.refresh(new_db_inbound_config)
    return new_db_inbound_config


def update_inbound_config(db: Session, db_inbound_config: InboundConfig, modify: InboundConfigModify):
    db_inbound_config.inbound_id = modify.inbound_id
    db_inbound_config.remark = modify.remark
    db_inbound_config.port = modify.port
    db_inbound_config.host = modify.host
    db_inbound_config.domain = modify.domain
    db_inbound_config.sni = modify.sni
    db_inbound_config.address = modify.address
    db_inbound_config.path = modify.path
    db_inbound_config.finger_print = modify.finger_print
    db_inbound_config.enable = modify.enable
    db_inbound_config.develop = modify.develop
    db_inbound_config.security = modify.security
    db_inbound_config.type = modify.type

    db.commit()
    db.refresh(db_inbound_config)

    return db_inbound_config


def get_inbound_configs(db: Session) -> Tuple[List[InboundConfig], int]:
    query = db.query(InboundConfig)

    query = query.order_by(InboundConfig.remark.asc())

    count = query.count()

    return query.all(), count


def remove_inbound_config(db: Session, db_inbound_config: InboundConfig):
    db.delete(db_inbound_config)
    db.commit()
    return db_inbound_config


def get_inbound_config(db: Session, inbound_config_id: int):
    return db.query(InboundConfig).filter(InboundConfig.id == inbound_config_id).first()
