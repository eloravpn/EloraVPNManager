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
from sqlalchemy.orm import relationship, mapped_column

from src.hosts.schemas import HostType
from src.inbounds.schemas import InboundSecurity, InboundType


class Inbound(Base):
    __tablename__ = "inbound"

    id = Column(Integer, primary_key=True, index=True)
    host_id = Column(Integer, ForeignKey("host.id"))
    host = relationship("Host", back_populates="inbounds")
    remark = Column(String(128), index=True)
    port = Column(Integer, index=True)
    domain = Column(String(128), index=True)
    request_host = Column(String(128), index=True)
    sni = Column(String(128), index=True)
    address = Column(String(128), index=True)
    path = Column(String(400))
    enable = Column(Boolean, default=True)
    develop = Column(Boolean, default=False)

    security = Column(
        Enum(InboundSecurity),
        unique=False,
        nullable=False,
        default=InboundSecurity.inbound_default.value,
    )

    type = Column(Enum(InboundType), nullable=False,
                  default=InboundType.VLESS)

    created_at = Column(DateTime, default=datetime.utcnow)
    modified_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
