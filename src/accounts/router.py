import datetime
import logging
import math
from typing import List

import humanize
from fastapi import APIRouter, Depends, HTTPException
from fastapi.openapi.models import Response
from pyasn1.type.univ import Integer
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

import src.accounts.service as service
import src.users.service as user_service
from src import config, messages
from src.accounts.schemas import (
    AccountCreate,
    AccountResponse,
    AccountModify,
    AccountsResponse,
    AccountUsedTrafficResponse,
    AccountsReport,
    AccountUsedTrafficReportResponse,
    AccountUedTrafficTrunc,
)
from src.admins.schemas import Admin
from src.database import get_db
from src.hosts.service import get_host_zone
from src.notification.schemas import NotificationCreate, NotificationType
from src.notification.service import create_notification

router = APIRouter()

logger = logging.getLogger("uvicorn.error")


@router.put("/accounts/bulk_extend", tags=["Account"])
def modify_account(
    db: Session = Depends(get_db),
    admin: Admin = Depends(Admin.get_current),
    pre_message_text: str = "",
    extend_day: int = 0,
    extend_data_limit_percent: int = 0,
):

    accounts, count = service.get_accounts(
        filter_enable=True, db=db, enable=True, test_account=False
    )

    total_extend_gb = 0

    for db_account in accounts:
        data_limit = db_account.data_limit
        used_traffic = db_account.used_traffic

        expire_date = db_account.expired_at

        if expire_date:
            extend_expire_date = expire_date + datetime.timedelta(days=extend_day)

        extend_data_limit_gb = 0
        extended_data_limit = 0

        if data_limit > 0 and extend_data_limit_percent > 0:
            extend_data_limit_gb = math.ceil(
                ((extend_data_limit_percent / 100) * (data_limit - used_traffic))
                / pow(1024, 3)
            )
            extended_data_limit = data_limit + (extend_data_limit_gb * pow(1024, 3))

            total_extend_gb += extend_data_limit_gb

            data_limit_readable = humanize.naturalsize(
                data_limit, binary=True, gnu=True, format="%.0f"
            )
            new_data_limit_readable = humanize.naturalsize(
                extended_data_limit, binary=True, gnu=True, format="%.0f"
            )
            logger.info(
                f"Service Traffic with id {db_account.email} owned by user:{db_account.user.full_name} "
                f"Extend from {data_limit_readable} To {new_data_limit_readable}"
            )
            logger.info(
                f"Service Expire Date with id {db_account.email} owned by user:{db_account.user.full_name} "
                f"Extend from {expire_date} To {extend_expire_date}"
            )

        account_modify = AccountModify(
            id=db_account.id,
            user_id=db_account.user_id,
            host_zone_id=db_account.host_zone_id,
            uuid=db_account.uuid,
            data_limit=extended_data_limit,
            used_traffic=db_account.used_traffic,
            ip_limit=db_account.ip_limit,
            email=db_account.email,
            enable=True,
            expired_at=extend_expire_date,
        )

        service.update_account(
            db=db,
            db_account=db_account,
            modify=account_modify,
            db_host_zone=db_account.host_zone,
        )

        message = pre_message_text + messages.USER_NOTIFICATION_ACCOUNT_EXTENDED.format(
            id=db_account.email,
            extend_day=extend_day,
            extend_data_limit_gb=extend_data_limit_gb,
            admin_id=config.TELEGRAM_ADMIN_USER_NAME,
        )

        create_notification(
            db=db,
            db_user=db_account.user,
            notification=NotificationCreate(
                user_id=db_account.user.id,
                approve=True,
                message=message,
                level=0,
                type=NotificationType.account,
            ),
        )

    return {"total": count, "total_extend_gb": total_extend_gb}


@router.post(
    "/accounts/{account_id}/reset_traffic",
    tags=["Account"],
    response_model=AccountResponse,
)
def add_account(
    account_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(Admin.get_current),
):
    db_account = service.get_account(db, account_id)
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")

    return service.reset_traffic(db=db, db_account=db_account)


@router.get(
    "/accounts/{account_id}/used_traffic",
    tags=["Account"],
    response_model=AccountUsedTrafficResponse,
)
def add_account(
    account_id: int,
    delta: int = None,
    db: Session = Depends(get_db),
    admin: Admin = Depends(Admin.get_current),
):
    db_account = service.get_account(db, account_id)
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")

    return service.get_account_used_traffic(db=db, db_account=db_account, delta=delta)


@router.get(
    "/accounts/used_traffic",
    tags=["Account"],
    response_model=AccountUsedTrafficResponse,
)
def add_account(
    delta: int = None,
    db: Session = Depends(get_db),
    admin: Admin = Depends(Admin.get_current),
):
    return service.get_all_accounts_used_traffic(db=db, delta=delta)


@router.get("/accounts/report", tags=["Account"], response_model=AccountsReport)
def get_accounts_report(
    db: Session = Depends(get_db), admin: Admin = Depends(Admin.get_current)
):
    active_accounts = service.get_accounts(
        db=db, filter_enable=True, enable=True, test_account=False
    )

    disabled_accounts = service.get_accounts(
        db=db, filter_enable=True, enable=False, test_account=False
    )

    total = active_accounts[1] + disabled_accounts[1]

    return AccountsReport(active=active_accounts[1], total=total)


@router.get(
    "/accounts/report_used_traffic",
    tags=["Account"],
    response_model=List[AccountUsedTrafficReportResponse],
)
def get_account_report_used_traffic(
    account_id: int,
    start_date: datetime.datetime,
    end_date: datetime.datetime,
    trunc: AccountUedTrafficTrunc = AccountUedTrafficTrunc.HOUR,
    db: Session = Depends(get_db),
    admin: Admin = Depends(Admin.get_current),
):
    return service.get_account_used_traffic_report(
        db=db,
        trunc=trunc,
        start_date=start_date,
        end_date=end_date,
        account_id=account_id,
    )


@router.post("/accounts/", tags=["Account"], response_model=AccountResponse)
def add_account(
    account: AccountCreate,
    db: Session = Depends(get_db),
    admin: Admin = Depends(Admin.get_current),
):
    db_user = user_service.get_user(db, account.user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db_host_zone = get_host_zone(db, host_zone_id=account.host_zone_id)
    if not db_host_zone:
        raise HTTPException(
            status_code=404,
            detail="Hose Zone not found with id " + account.host_zone_id,
        )

    try:
        db_account = service.create_account(
            db=db, db_user=db_user, account=account, db_host_zone=db_host_zone
        )
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Account already exists")

    return db_account


@router.put("/accounts/{account_id}", tags=["Account"], response_model=AccountResponse)
def modify_account(
    account_id: int,
    account: AccountModify,
    db: Session = Depends(get_db),
    admin: Admin = Depends(Admin.get_current),
):
    db_account = service.get_account(db, account_id)
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")

    db_host_zone = get_host_zone(db, host_zone_id=account.host_zone_id)
    if not db_host_zone:
        raise HTTPException(
            status_code=404,
            detail="Hose Zone not found with id " + account.host_zone_id,
        )

    return service.update_account(
        db=db, db_account=db_account, modify=account, db_host_zone=db_host_zone
    )


@router.get("/accounts/{account_id}", tags=["Account"], response_model=AccountResponse)
def get_account(
    account_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(Admin.get_current),
):
    db_account = service.get_account(db, account_id)
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")

    return db_account


@router.delete("/accounts/{account_id}", tags=["Account"])
def delete_account(
    account_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(Admin.get_current),
):
    db_account = service.get_account(db, account_id)
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")

    service.remove_account(db=db, db_account=db_account)
    return {}


@router.get("/accounts/", tags=["Account"], response_model=AccountsResponse)
def get_accounts(
    offset: int = None,
    limit: int = None,
    sort: str = None,
    enable: bool = True,
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
                sort.append(service.AccountSortingOptions[opt])
            except KeyError:
                raise HTTPException(
                    status_code=400, detail=f'"{opt}" is not a valid sort option'
                )

    accounts, count = service.get_accounts(
        filter_enable=True,
        db=db,
        enable=enable,
        user_id=user_id,
        offset=offset,
        limit=limit,
        sort=sort,
        q=q,
    )

    return {"accounts": accounts, "total": count}
