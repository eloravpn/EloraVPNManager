import logging
from sqlite3 import IntegrityError

from fastapi import APIRouter, Depends, HTTPException
from fastapi.openapi.models import Response
from pyasn1.type.univ import Integer
from sqlalchemy.orm import Session

import src.accounts.service as service
import src.users.service as user_service
from src.accounts.schemas import AccountCreate, AccountResponse, AccountModify, AccountsResponse, \
    AccountUsedTrafficResponse, AccountsReport
from src.admins.schemas import Admin
from src.database import get_db

router = APIRouter()

logger = logging.getLogger('uvicorn.error')


@router.post("/accounts/{account_id}/reset_traffic", tags=["Account"], response_model=AccountResponse)
def add_account(account_id: int,
                db: Session = Depends(get_db),
                admin: Admin = Depends(Admin.get_current)):
    db_account = service.get_account(db, account_id)
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")

    return service.reset_traffic(db=db, db_account=db_account)


@router.get("/accounts/{account_id}/used_traffic", tags=["Account"], response_model=AccountUsedTrafficResponse)
def add_account(account_id: int,
                delta: int = None,
                db: Session = Depends(get_db),
                admin: Admin = Depends(Admin.get_current)):
    db_account = service.get_account(db, account_id)
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")

    return service.get_account_used_traffic(db=db, db_account=db_account, delta=delta)


@router.get("/accounts/used_traffic", tags=["Account"], response_model=AccountUsedTrafficResponse)
def add_account(delta: int = None,
                db: Session = Depends(get_db),
                admin: Admin = Depends(Admin.get_current)):

    return service.get_all_accounts_used_traffic(db=db, delta=delta)


@router.get("/accounts/report", tags=['Account'], response_model=AccountsReport)
def get_accounts_report(db: Session = Depends(get_db), admin: Admin = Depends(Admin.get_current)):
    active_accounts = service.get_accounts(
        db=db,
        filter_enable=True,
        enable=True,
        test_account=False
    )

    disabled_accounts = service.get_accounts(
        db=db,
        filter_enable=True,
        enable=False,
        test_account=False
    )

    total = active_accounts[1] + disabled_accounts[1]

    return AccountsReport(active=active_accounts[1], total=total)


@router.post("/accounts/", tags=["Account"], response_model=AccountResponse)
def add_account(account: AccountCreate,
                db: Session = Depends(get_db),
                admin: Admin = Depends(Admin.get_current)):
    db_user = user_service.get_user(db, account.user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    logger.info(f"Account expired at {account.expired_at}")
    logger.info(f"Account data limit  {account.data_limit}")

    try:
        db_account = service.create_account(db=db, db_user=db_user, account=account)
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Account already exists")

    return db_account


@router.put("/accounts/{account_id}", tags=["Account"], response_model=AccountResponse)
def modify_account(account_id: int, account: AccountModify,
                   db: Session = Depends(get_db),
                   admin: Admin = Depends(Admin.get_current)):
    db_account = service.get_account(db, account_id)
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")

    return service.update_account(db=db, db_account=db_account, modify=account)


@router.get("/accounts/{account_id}", tags=["Account"],
            response_model=AccountResponse)
def get_account(account_id: int, db: Session = Depends(get_db),
                admin: Admin = Depends(Admin.get_current)):
    db_account = service.get_account(db, account_id)
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")

    return db_account


@router.delete("/accounts/{account_id}", tags=["Account"])
def delete_account(account_id: int, db: Session = Depends(get_db),
                   admin: Admin = Depends(Admin.get_current)):
    db_account = service.get_account(db, account_id)
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")

    service.remove_account(db=db, db_account=db_account)
    return {}


@router.get("/accounts/", tags=['Account'], response_model=AccountsResponse)
def get_accounts(
        offset: int = None,
        limit: int = None,
        sort: str = None,
        enable: bool = True,
        db: Session = Depends(get_db),
        admin: Admin = Depends(Admin.get_current)
):
    if sort is not None:
        opts = sort.strip(',').split(',')
        sort = []
        for opt in opts:
            try:
                sort.append(service.AccountSortingOptions[opt])
            except KeyError:
                raise HTTPException(status_code=400,
                                    detail=f'"{opt}" is not a valid sort option')

    accounts, count = service.get_accounts(
        filter_enable=True,
        db=db,
        enable=enable,
        offset=offset,
        limit=limit,
        sort=sort
    )

    return {"accounts": accounts, "total": count}
