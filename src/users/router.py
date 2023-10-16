from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

import src.users.service as service
from src.admins.schemas import Admin
from src.database import get_db
from src.users.schemas import UserCreate, UserResponse, UserModify, UsersResponse

router = APIRouter()


@router.post("/users/", tags=["User"], response_model=UserResponse)
def add_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    admin: Admin = Depends(Admin.get_current),
):
    try:
        db_user = service.create_user(db=db, user=user)

    except IntegrityError as error:
        raise HTTPException(status_code=409, detail="User already exists")

    return db_user


@router.put("/users/{user_id}", tags=["User"], response_model=UserResponse)
def modify_user(
    user_id: int,
    user: UserModify,
    db: Session = Depends(get_db),
    admin: Admin = Depends(Admin.get_current),
):
    db_user = service.get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    return service.update_user(db=db, db_user=db_user, modify=user)


@router.get("/users/{user_id}", tags=["User"], response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(Admin.get_current),
):
    db_user = service.get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    return db_user


@router.delete("/users/{user_id}", tags=["User"])
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(Admin.get_current),
):
    db_user = service.get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    service.remove_user(db=db, db_user=db_user)
    return {}


@router.get("/users/", tags=["User"], response_model=UsersResponse)
def get_users(
    offset: int = None,
    limit: int = None,
    sort: str = None,
    enable: int = -1,
    q: str = None,
    db: Session = Depends(get_db),
    admin: Admin = Depends(Admin.get_current),
):
    if sort is not None:
        opts = sort.strip(",").split(",")
        sort = []
        for opt in opts:
            try:
                sort.append(service.UserSortingOptions[opt])
            except KeyError:
                raise HTTPException(
                    status_code=400, detail=f'"{opt}" is not a valid sort option'
                )

    users, count = service.get_users(
        db=db, limit=limit, offset=offset, q=q, sort=sort, enable=enable
    )

    return {"users": users, "total": count}
