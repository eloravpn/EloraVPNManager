from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Boolean,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from src.database import Base
from src.inbounds.schemas import InboundSecurity, InboundType


class Inbound(Base):
    __tablename__ = "inbound"
    __table_args__ = (UniqueConstraint("host_id", "key"),)

    id = Column(Integer, primary_key=True, index=True)
    host_id = Column(Integer, ForeignKey("host.id"))
    inbound_configs = relationship(
        "InboundConfig", back_populates="inbound", cascade="all, delete-orphan"
    )
    host = relationship("Host", back_populates="inbounds")
    key = Column(Integer, index=True, nullable=False)
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
        default=InboundSecurity.default.value,
    )

    type = Column(Enum(InboundType), nullable=False, default=InboundType.default.value)

    created_at = Column(DateTime, default=datetime.utcnow)
    modified_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
