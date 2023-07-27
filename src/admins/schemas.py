from enum import Enum
from typing import List

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, root_validator, validator
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from src.config import SUDOERS
from src.database import get_db
from src.utils.jwt import get_admin_payload

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/admin/token")  # Admin view url


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class Admin(BaseModel):
    username: str
    is_sudo: bool = False

    @classmethod
    def get_current(cls,
                    db: Session = Depends(get_db),
                    token: str = Depends(oauth2_scheme)):

        exc = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        payload = get_admin_payload(token)
        if not payload:
            raise exc

        if payload['username'] in SUDOERS and payload['is_sudo'] is True:
            return cls(username=payload['username'], is_sudo=True)

        # dbadmin = crud.get_admin(db, payload['username'])
        # if not dbadmin:
        #     raise exc

        # return cls.from_orm(dbadmin)
