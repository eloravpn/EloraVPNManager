from datetime import datetime
import re

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    Boolean,
)
from sqlalchemy.orm import relationship, validates

from src.database import Base

USERNAME_REGEXP = re.compile(r'^(?=\w{3,32}\b)[a-zA-Z0-9]+(?:_[a-zA-Z0-9]+)*$')

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    accounts = relationship("Account", back_populates="user", cascade="all, delete-orphan")
    username = Column(String(128), unique=True, index=True, nullable=False)
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

    @validates('username')
    def validate_username(self, key, username):
        if not USERNAME_REGEXP.match(username):
            raise ValueError(
                'Username only can be 3 to 32 characters and contain a-z, 0-9, and underscores in between.')

        return username
