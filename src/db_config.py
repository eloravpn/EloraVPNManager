from decouple import config
from dotenv import load_dotenv

load_dotenv()

SQLALCHEMY_DATABASE_URL = config(
    "SQLALCHEMY_DATABASE_URL", default="sqlite:///db.sqlite3"
)
