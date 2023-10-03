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
from sqlalchemy.orm import relationship

from src.database import Base
from src.notification.schemas import (
    NotificationEngine,
    NotificationStatus,
    NotificationType,
)


class Notification(Base):
    __tablename__ = "notification"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("account.id"), nullable=True)
    account = relationship("Account", back_populates="notification")
    level = Column(Integer, index=True)
    message = Column(String(4096))
    details = Column(String(10000))

    approve = Column(Boolean, default=True)

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
