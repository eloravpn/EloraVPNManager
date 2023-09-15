from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    Boolean,
    ForeignKey,
    BigInteger,
    case,
)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, validates

from src.database import Base


class Account(Base):
    __tablename__ = "account"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", back_populates="accounts")
    used_traffic_history = relationship(
        "AccountUsedTraffic", back_populates="account", cascade="all, delete-orphan"
    )
    notification = relationship(
        "Notification", back_populates="account", cascade="all, delete-orphan"
    )
    orders = relationship("Order", back_populates="account")
    uuid = Column(String(128), index=True, unique=True, nullable=False)
    email = Column(String(128), index=True, unique=True, nullable=False)
    enable = Column(Boolean, default=True)
    used_traffic = Column(BigInteger, default=0)
    data_limit = Column(BigInteger, nullable=True)

    expired_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    modified_at = Column(DateTime, default=datetime.utcnow)

    @hybrid_property
    def used_traffic_percent(self):
        if self.data_limit > 0:
            return 100 * (self.used_traffic / self.data_limit)
        else:
            return 0

    @hybrid_property
    def full_name(self):
        if self.user:
            return self.user.full_name
        else:
            return None

    @used_traffic_percent.expression
    def used_traffic_percent(cls):
        return case(
            (cls.data_limit > 0, 100 * (cls.used_traffic / cls.data_limit)),
            else_=0,
        )

    @validates("uuid")
    def validate_uuid(self, key, uuid):
        UUID(uuid, version=4)
        return uuid


class AccountUsedTraffic(Base):
    __tablename__ = "account_used_traffic"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("account.id"))
    account = relationship("Account", back_populates="used_traffic_history")
    download = Column(BigInteger, default=0)
    upload = Column(BigInteger, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
