import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import src.notification.service as notification_service
from src.admins.schemas import Admin
from src.database import get_db
from src.notification.schemas import (
    NotificationsResponse,
    NotificationStatus,
    NotificationType,
)

notification_router = APIRouter()

logger = logging.getLogger("uvicorn.error")


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
