from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel


class NotificationEngine(str, Enum):
    telegram = "telegram"
    email = "email"
    sms = "sms"


class NotificationStatus(str, Enum):
    pending = "pending"
    canceled = "canceled"
    failed = "failed"
    sent = "sent"


class NotificationType(str, Enum):
    payment = "payment"
    order = "order"
    transaction = "transaction"
    general = "general"
    account = "account"
    used_traffic = "used_traffic"
    expire_time = "expire_time"


class NotificationUsedTrafficLevel(int, Enum):
    fifty_percent = 50
    eighty_percent = 80
    ninety_five_percent = 95
    full_percent_used = 100


class NotificationExpireTimeLevel(int, Enum):
    thirty_day = 1
    seven_day = 2
    three_day = 3
    one_day = 4
    expired = 5


class NotificationBase(BaseModel):
    level: int
    message: str = None
    details: str = None

    approve: bool = False

    engine: Optional[NotificationEngine] = NotificationEngine.telegram
    status: Optional[NotificationStatus] = NotificationStatus.pending
    type: NotificationType


class NotificationCreate(NotificationBase):
    pass


class NotificationModify(NotificationBase):
    id: int


class NotificationResponse(NotificationBase):
    id: int
    account_id: Optional[int] = None
    user_id: Optional[int] = None

    created_at: datetime
    modified_at: datetime

    def dict(cls, *args, **kwargs):
        return super().dict(*args, **kwargs)

    class Config:
        orm_mode = True


class NotificationsResponse(BaseModel):
    inbound_configs: List[NotificationResponse]
    total: int
