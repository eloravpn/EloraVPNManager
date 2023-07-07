from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    Boolean,
)
from sqlalchemy.orm import relationship

from src.database import Base


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    accounts = relationship("Account", back_populates="user")
    username = Column(String(128), unique=True, index=True)
    hashed_password = Column(String(128))
    first_name = Column(String(128), index=True)
    last_name = Column(String(128), index=True)
    description = Column(String(4000))
    telegram_chat_id = Column(Integer, unique=True, )
    telegram_username = Column(String(128), unique=True, index=True)
    phone_number = Column(String(128), unique=True, index=True)

    enable = Column(Boolean, default=True)
    banned = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    modified_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
