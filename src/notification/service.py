from enum import Enum
from typing import List, Tuple, Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session

from src.accounts.models import Account
from src.notification.models import Notification
from src.notification.schemas import (
    NotificationStatus,
    NotificationType,
    NotificationCreate,
)

NotificationSortingOptions = Enum(
    "NotificationSortingOptions",
    {
        "created": Notification.created_at.asc(),
        "-created": Notification.created_at.desc(),
        "modified": Notification.modified_at.asc(),
        "-modified": Notification.modified_at.desc(),
        "type": Notification.type.asc(),
        "-type": Notification.type.desc(),
        "engine": Notification.engine.asc(),
        "-engine": Notification.engine.desc(),
        "level": Notification.level.asc(),
        "-level": Notification.level.desc(),
        "status": Notification.status.asc(),
        "-status": Notification.status.desc(),
        "approve": Notification.approve.asc(),
        "-approve": Notification.approve.desc(),
    },
)


def create_notification(
    db: Session, db_account: Account, notification: NotificationCreate
):
    db_notification = Notification(
        account_id=db_account.id,
        level=notification.level,
        message=notification.message,
        details=notification.details,
        approve=notification.approve,
        status=notification.status,
        engine=notification.engine,
        type=notification.type,
    )

    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification


def update_status(
    db: Session,
    db_notification: Notification,
    status: NotificationStatus,
    approve: bool,
):
    db_notification.status = status.value
    db_notification.approve = approve

    db.commit()
    db.refresh(db_notification)

    return db_notification


def get_notifications(
    db: Session,
    offset: Optional[int] = None,
    limit: Optional[int] = None,
    sort: Optional[List[NotificationSortingOptions]] = [
        NotificationSortingOptions["-modified"]
    ],
    q: str = None,
    approve: int = -1,
    account_id: int = 0,
    notification_type: NotificationType = None,
    level: int = 0,
    status: NotificationStatus = None,
    return_with_count: bool = True,
) -> Tuple[List[Notification], int]:
    query = db.query(Notification)

    if approve >= 0:
        query = query.filter(Notification.approve == (True if approve > 0 else False))

    if account_id > 0:
        query = query.filter(Notification.account_id == account_id)

    if level > 0:
        query = query.filter(Notification.level == level)

    if notification_type:
        query = query.filter(Notification.type == notification_type)

    if status:
        query = query.filter(Notification.status == status)

    if q:
        query = query.filter(
            or_(
                Notification.message.ilike(f"%{q}%"),
                Notification.details.ilike(f"%{q}%"),
            )
        )

    if sort:
        query = query.order_by(*(opt.value for opt in sort))

    count = query.count()

    if offset:
        query = query.offset(offset)
    if limit:
        query = query.limit(limit)

    if return_with_count:
        return query.all(), count
    else:
        return query.all()


def remove_notification(db: Session, db_notification: Notification):
    db.delete(db_notification)
    db.commit()
    return db_notification


def get_notification(db: Session, notification_id: int) -> Notification:
    return db.query(Notification).filter(Notification.id == notification_id).first()
