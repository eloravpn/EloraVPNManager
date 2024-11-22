from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from src.db_config import SQLALCHEMY_DATABASE_URL

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args=(
        {"check_same_thread": False}
        if SQLALCHEMY_DATABASE_URL.startswith("sqlite")
        else {}
    ),
)

SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, expire_on_commit=False, bind=engine
)


class GetDB:  # Context Manager
    def __init__(self):
        self.db = SessionLocal()

    def __enter__(self):
        return self.db

    def __exit__(self, exc_type, exc_value, traceback):
        self.db.close()


def get_db():  # Dependency
    with GetDB() as db:
        yield db


Base = declarative_base()
