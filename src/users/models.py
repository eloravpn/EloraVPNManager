from datetime import datetime
import re

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    Boolean,
    BigInteger,
)
from sqlalchemy.orm import relationship, validates
from telebot.formatting import escape_markdown

from src.database import Base

USERNAME_REGEXP = re.compile(r"^(?=\w{3,32}\b)[a-zA-Z0-9]+(?:_[a-zA-Z0-9]+)*$")


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    accounts = relationship(
        "Account", back_populates="user", cascade="all, delete-orphan"
    )
    referral_user_id = Column(Integer, index=True, nullable=True)
    orders = relationship("Order", back_populates="user")
    payments = relationship("Payment", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")
    notification = relationship(
        "Notification", back_populates="user", cascade="all, delete-orphan"
    )
    club_scores = relationship(
        "ClubScore", back_populates="user", cascade="all, delete-orphan"
    )
    club_profile = relationship(
        "ClubProfile",
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False,
    )
    username = Column(String(128), unique=True, index=True, nullable=False)
    hashed_password = Column(String(128))
    first_name = Column(String(128), index=True, nullable=True)
    last_name = Column(String(128), index=True, nullable=True)
    description = Column(String(4000), nullable=True)
    telegram_chat_id = Column(BigInteger, unique=True, nullable=True)
    telegram_username = Column(String(128), index=True, unique=True, nullable=True)
    phone_number = Column(String(128), index=True, unique=True, nullable=True)
    email_address = Column(String(128), index=True, unique=True, nullable=True)
    balance = Column(BigInteger, default=0)

    enable = Column(Boolean, default=True)
    banned = Column(Boolean, default=False)
    force_join_channel = Column(
        Boolean, default=True, nullable=False, server_default="true"
    )

    created_at = Column(DateTime, default=datetime.utcnow)
    modified_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @validates("username")
    def validate_username(self, key, username):
        if not USERNAME_REGEXP.match(username):
            raise ValueError(
                "Username only can be 3 to 32 characters and contain a-z, 0-9, and underscores in between."
            )

        return username

    @property
    def full_name(self):
        full_name = self.first_name
        if self.last_name:
            full_name += " {0}".format(self.last_name)
        return escape_markdown(full_name)

    @property
    def telegram_profile_full(self):
        return f"👤 {self.full_name} (<code>{self.telegram_username}</code>)[<code>{self.telegram_chat_id}</code>]"

    @property
    def balance_readable(self):
        if self.balance:
            return f"{self.balance:,}"
        else:
            return 0
