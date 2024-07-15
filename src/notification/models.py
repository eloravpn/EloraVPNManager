from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Boolean,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from src.database import Base
from src.notification.schemas import (
    NotificationEngine,
    NotificationStatus,
    NotificationType,
)

from sqlalchemy_json import mutable_json_type


class Notification(Base):
    __tablename__ = "notification"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=True)
    user = relationship("User", back_populates="notification")
    account_id = Column(Integer, ForeignKey("account.id"), nullable=True)
    account = relationship("Account", back_populates="notification")
    level = Column(Integer, index=True)
    message = Column(String(4096))
    keyboard = Column(mutable_json_type(dbtype=JSONB, nested=True), nullable=True)
    photo_url = Column(String(400), nullable=True)
    details = Column(String(10000))

    approve = Column(Boolean, default=True)
    send_to_admin = Column(Boolean, default=True)

    engine = Column(
        Enum(NotificationEngine),
        unique=False,
        nullable=False,
        default=NotificationEngine.telegram.value,
    )

    status = Column(
        Enum(NotificationStatus),
        unique=False,
        nullable=False,
        default=NotificationStatus.pending.value,
    )

    type = Column(Enum(NotificationType), unique=False, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    modified_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
