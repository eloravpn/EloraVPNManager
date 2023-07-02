import os
from datetime import datetime

from src.database import Base
from sqlalchemy import (
    JSON,
    BigInteger,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Table,
    UniqueConstraint, Boolean,
)
from sqlalchemy.orm import relationship

from src.hosts.schemas import HostType
from src.inbounds.schemas import InboundSecurity, InboundType


class InboundConfig(Base):
    __tablename__ = "inbound_config"

    id = Column(Integer, primary_key=True, index=True)
    inbound_id = Column(Integer, ForeignKey("inbound.id"), nullable=True)
    remark = Column(String(128), index=True)
    port = Column(Integer, index=True)
    domain = Column(String(128), index=True)
    host = Column(String(128), index=True)
    sni = Column(String(128), index=True)
    address = Column(String(128), index=True)
    path = Column(String(400))
    enable = Column(Boolean, default=True)
    dev_mode = Column(Boolean,default=False)


    security = Column(
        Enum(InboundSecurity),
        unique=False,
        nullable=False,
        default=InboundSecurity.inbound_default.value,
    )

    inbound_type = Column(Enum(InboundType), nullable=False,
                  default=InboundType.VLESS)

    created_at = Column(DateTime, default=datetime.utcnow)
