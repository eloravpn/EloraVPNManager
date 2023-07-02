from fastapi import APIRouter, Depends, HTTPException
from fastapi import status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.admins.schemas import Token
from src.config import SUDOERS
from src.database import get_db
from src.utils.jwt import create_admin_token

router = APIRouter()


def authenticate_sudo(username: str, password: str):
    try:
        return password == SUDOERS[username]
    except KeyError:
        return False


def authenticate_admin(db: Session, username: str, password: str):
    if password == 'admin':
        return True
    else:
        return False


@router.post("/admin/token", tags=['Admin'], response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(),
                           db: Session = Depends(get_db)):
    if authenticate_sudo(form_data.username, form_data.password):
        return Token(access_token=create_admin_token(form_data.username, is_sudo=True))

    if authenticate_admin(db, form_data.username, form_data.password):
        return Token(access_token=create_admin_token(form_data.username))

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )
