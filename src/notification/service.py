import json
from enum import Enum
from typing import List, Tuple, Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session

import src.accounts.service as account_service
import src.users.service as user_service
from src.accounts.models import Account
from src.notification.models import Notification
from src.notification.schemas import (
    NotificationStatus,
    NotificationType,
    NotificationCreate,
    NotificationModify,
)
from src.users.models import User

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
    db: Session,
    notification: NotificationCreate,
    db_account: Optional[Account] = None,
    db_user: Optional[User] = None,
):
    db_notification = Notification(
        account_id=None if db_account is None else db_account.id,
        user_id=None if db_user is None else db_user.id,
        level=notification.level,
        message=notification.message,
        details=notification.details,
        approve=notification.approve,
        send_to_admin=notification.send_to_admin,
        status=notification.status,
        engine=notification.engine,
        type=notification.type,
        keyboard=(json.loads(notification.keyboard) if notification.keyboard else None),
        photo_url=notification.photo_url,
    )

    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification


def create_bulk_notification(
    db: Session,
    user_ids: Optional[List[int]],
    notification: NotificationCreate,
):
    for user_id in user_ids:
        db_notification = Notification(
            account_id=None,
            user_id=user_id,
            level=notification.level,
            message=notification.message,
            details=notification.details,
            approve=notification.approve,
            send_to_admin=notification.send_to_admin,
            status=notification.status,
            engine=notification.engine,
            type=notification.type,
            keyboard=(
                json.loads(notification.keyboard)
                if notification.keyboard is not None
                else None
            ),
            photo_url=notification.photo_url,
        )

        db.add(db_notification)

    db.commit()


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
    user_id: int = 0,
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

    if user_id > 0:
        query = query.filter(Notification.user_id == user_id)

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


def _validate_notification(
    db: Session,
    db_user: User,
    db_notification: Notification,
    modify: NotificationModify,
):
    db_account = account_service.get_account(db=db, account_id=modify.account_id)

    if db_account and db_account.user_id != db_user.id:
        # TODO: create new exception
        raise Exception


def update_notification(
    db: Session, db_notification: Notification, modify: NotificationModify
):
    db_user = user_service.get_user(db, db_notification.user_id)

    _validate_notification(
        db=db, db_user=db_user, db_notification=db_notification, modify=modify
    )

    db_notification.account_id = modify.account_id
    db_notification.user_id = modify.user_id
    db_notification.level = modify.level
    db_notification.message = modify.message
    db_notification.approve = modify.approve
    db_notification.engine = modify.engine
    db_notification.status = modify.status
    db_notification.type = modify.type

    db_notification.keyboard = (
        json.loads(modify.keyboard) if modify.keyboard is not None else None
    )
    db_notification.photo_url = modify.photo_url

    db.commit()
    db.refresh(db_notification)

    return db_notification


def remove_notification(db: Session, db_notification: Notification):
    db.delete(db_notification)
    db.commit()
    return db_notification


def get_notification(db: Session, notification_id: int) -> Notification:
    return db.query(Notification).filter(Notification.id == notification_id).first()
