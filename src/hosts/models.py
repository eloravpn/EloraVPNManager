from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    Integer,
    String,
    Boolean,
)
from sqlalchemy.orm import relationship

from src.database import Base
from src.hosts.schemas import HostType


class Host(Base):
    __tablename__ = "host"

    id = Column(Integer, primary_key=True, index=True)
    inbounds = relationship("Inbound", back_populates="host", cascade="all, delete-orphan")
    name = Column(String(128), index=True)
    domain = Column(String(128), unique=True, index=True)
    username = Column(String(34, collation='NOCASE'))
    password = Column(String(128))
    ip = Column(String(128), unique=True, index=True)
    port = Column(Integer, index=True)
    api_path = Column(String(400))
    enable = Column(Boolean, default=True)
    master = Column(Boolean, default=False)

    type = Column(Enum(HostType), nullable=False,
                  default=HostType.x_ui_sanaei)

    created_at = Column(DateTime, default=datetime.utcnow)
    modified_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
