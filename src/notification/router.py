import logging
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

import src.accounts.service as account_service
import src.notification.service as notification_service
import src.users.service as user_service
from src.admins.schemas import Admin
from src.database import get_db
from src.exc import EloraApplicationError
from src.notification.schemas import (
    NotificationsResponse,
    NotificationStatus,
    NotificationType,
    NotificationResponse,
    NotificationCreate,
    NotificationModify,
)

notification_router = APIRouter()

from src.logger import logger


@notification_router.get(
    "/notifications/", tags=["Notification"], response_model=NotificationsResponse
)
def get_notifications(
    offset: int = None,
    limit: int = None,
    sort: str = None,
    approve: int = -1,
    status: NotificationStatus = None,
    type_: NotificationType = None,
    account_id: int = 0,
    user_id: int = 0,
    q: str = None,
    db: Session = Depends(get_db),
    admin: Admin = Depends(Admin.get_current),
):
    if sort is not None:
        opts = sort.strip(",").split(",")
        sort = []
        for opt in opts:
            try:
                sort.append(notification_service.NotificationSortingOptions[opt])
            except KeyError:
                raise HTTPException(
                    status_code=400, detail=f'"{opt}" is not a valid sort option'
                )

    notifications, count = notification_service.get_notifications(
        db=db,
        offset=offset,
        limit=limit,
        sort=sort,
        status=status,
        approve=approve,
        account_id=account_id,
        user_id=user_id,
        notification_type=type_,
        q=q,
    )

    return {"notifications": notifications, "total": count}


@notification_router.post("/notifications/bulk_send", tags=["Notification"])
def bulk_send_notification(
    user_ids: Optional[List[int]],
    notification: NotificationCreate,
    db: Session = Depends(get_db),
    admin: Admin = Depends(Admin.get_current),
):
    try:
        notification_service.create_bulk_notification(
            db=db,
            user_ids=user_ids,
            notification=notification,
        )
    except IntegrityError as error:
        logger.error(error)
        raise HTTPException(status_code=409, detail="Error in create notifications")
    except EloraApplicationError as error:
        raise HTTPException(status_code=409, detail=error.message())


@notification_router.post(
    "/notifications/", tags=["Notification"], response_model=NotificationResponse
)
def add_notification(
    notification: NotificationCreate,
    db: Session = Depends(get_db),
    admin: Admin = Depends(Admin.get_current),
):
    db_user = user_service.get_user(db, notification.user_id)

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db_account = None

    if notification.account_id and notification.account_id != 0:
        db_account = account_service.get_account(
            db=db, account_id=notification.account_id
        )

        if not db_account:
            raise HTTPException(status_code=404, detail="Account not found")

    try:
        db_notification = notification_service.create_notification(
            db=db,
            db_user=db_user,
            db_account=db_account if db_account else None,
            notification=notification,
        )
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Notification already exists")
    except EloraApplicationError as error:
        raise HTTPException(status_code=409, detail=error.message())

    return db_notification


@notification_router.put(
    "/notifications/{notification_id}",
    tags=["Notification"],
    response_model=NotificationResponse,
)
def modify_notification(
    notification_id: int,
    notification: NotificationModify,
    db: Session = Depends(get_db),
    admin: Admin = Depends(Admin.get_current),
):
    db_notification = notification_service.get_notification(
        db, notification_id=notification_id
    )
    if not db_notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    return notification_service.update_notification(
        db=db, db_notification=db_notification, modify=notification
    )


@notification_router.delete("/notifications/{notification_id}", tags=["Notification"])
def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(Admin.get_current),
):
    db_notification = notification_service.get_notification(
        db, notification_id=notification_id
    )
    if not db_notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    notification_service.remove_notification(db=db, db_notification=db_notification)

    return {}
