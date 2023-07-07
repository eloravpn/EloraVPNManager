from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    Boolean, ForeignKey,
)
from sqlalchemy.orm import relationship

from src.database import Base


class Account(Base):
    __tablename__ = "account"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"))

    user = relationship("User", back_populates="accounts")
    uuid = Column(String(128), index=True, unique=True, nullable=False)
    email = Column(String(128), index=True, unique=True, nullable=False)
    enable = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    modified_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
