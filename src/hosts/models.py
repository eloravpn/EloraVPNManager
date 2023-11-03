from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    Integer,
    String,
    Boolean,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from src.database import Base
from src.hosts.schemas import HostType


class Host(Base):
    __tablename__ = "host"

    id = Column(Integer, primary_key=True, index=True)
    inbounds = relationship(
        "Inbound", back_populates="host", cascade="all, delete-orphan"
    )
    host_zone_id = Column(Integer, ForeignKey("host_zone.id"), nullable=False)
    host_zone = relationship("HostZone", back_populates="hosts")

    name = Column(String(128), index=True)
    domain = Column(String(128), unique=True, index=True)
    username = Column(String(34))
    password = Column(String(128))
    ip = Column(String(128), unique=True, index=True)
    port = Column(Integer, index=True)
    api_path = Column(String(400))
    enable = Column(Boolean, default=True)
    master = Column(Boolean, default=False)

    type = Column(Enum(HostType), nullable=False, default=HostType.x_ui_sanaei)

    created_at = Column(DateTime, default=datetime.utcnow)
    modified_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class HostZone(Base):
    __tablename__ = "host_zone"

    hosts = relationship(
        "Host", back_populates="host_zone", cascade="all, delete-orphan"
    )
    accounts = relationship("Account", back_populates="host_zone")
    services = relationship("Service", back_populates="host_zone")
    orders = relationship("Order", back_populates="host_zone")

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128), index=True)
    description = Column(String(4000), index=True)
    max_account = Column(Integer, index=True, default=0)
    enable = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    modified_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
