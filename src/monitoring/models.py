from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    Boolean,
)

from src.database import Base


class MonitoringResult(Base):
    __tablename__ = "monitoring_result"

    id = Column(Integer, primary_key=True, index=True)
    # host_id = Column(Integer, ForeignKey("host.id"))
    # host = relationship("Host", back_populates="inbounds")

    client_name = Column(String(128), index=True)
    client_ip = Column(String(128), index=True)
    test_url = Column(String(128), index=True)
    remark = Column(String(128), index=True)
    port = Column(Integer, index=True)
    domain = Column(String(128), index=True)
    sni = Column(String(128), index=True)
    delay = Column(Integer, index=False)
    ping = Column(Integer, index=False)

    develop = Column(Boolean, default=False)
    success = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    modified_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
