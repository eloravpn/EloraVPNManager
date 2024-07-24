import logging

import requests
from decouple import config
from dotenv import load_dotenv

load_dotenv()

# Disable IPv6
requests.packages.urllib3.util.connection.HAS_IPV6 = False

DEBUG = config("DEBUG", default=False, cast=bool)
DOCS = config("DOCS", default=False, cast=bool)
# Set log level based on python logging module
LOG_LEVEL = config("LOG_LEVEL", default=logging.INFO, cast=int)

SERVER_IP = "127.0.0.1"

if not DEBUG:
    try:
        SERVER_IP = requests.get("https://api.ipify.org", timeout=5).text.strip()
    except requests.exceptions.RequestException:
        print("Failed to get SERVER_IP, using 127.0.0.1 instead")
        SERVER_IP = "127.0.0.1"

SQLALCHEMY_DATABASE_URL = config(
    "SQLALCHEMY_DATABASE_URL", default="sqlite:///db.sqlite3"
)

UVICORN_HOST = config("UVICORN_HOST", default="0.0.0.0")
UVICORN_PORT = config("UVICORN_PORT", cast=int, default=8000)
UVICORN_UDS = config("UVICORN_UDS", default=None)
UVICORN_SSL_CERTFILE = config("UVICORN_SSL_CERTFILE", default=None)
UVICORN_SSL_KEYFILE = config("UVICORN_SSL_KEYFILE", default=None)

TELEGRAM_API_TOKEN = config("TELEGRAM_API_TOKEN", default=None)
TELEGRAM_PAYMENT_API_TOKEN = config("TELEGRAM_PAYMENT_API_TOKEN", default=None)
TELEGRAM_ADMIN_ID = config("TELEGRAM_ADMIN_ID", cast=int, default=0)
TELEGRAM_ADMIN_USER_NAME = config("TELEGRAM_ADMIN_USER_NAME", default=None)
BOT_USER_NAME = config("BOT_USER_NAME", default="")
TELEGRAM_CHANNEL = config("TELEGRAM_CHANNEL", default=None)
TELEGRAM_PROXY_URL = config("TELEGRAM_PROXY_URL", default=None)
MINIMUM_PAYMENT_TO_TRUST_USER = config(
    "MINIMUM_PAYMENT_TO_TRUST_USER", cast=int, default=200000
)
TRUST_CARD_NUMBER = config("TRUST_CARD_NUMBER", default="")
TRUST_CARD_OWNER = config("TRUST_CARD_OWNER", default="")
CARD_NUMBER = config("CARD_NUMBER", default="")
CARD_OWNER = config("CARD_OWNER", default="")

TEST_ACCOUNT_EMAIL_PREFIX = config("TEST_ACCOUNT_EMAIL_PREFIX", default="test_")
TEST_ACCOUNT_LIMIT_INTERVAL_DAYS = config(
    "TEST_ACCOUNT_LIMIT_INTERVAL_DAYS", cast=int, default=3
)
TEST_ACCOUNT_DATA_LIMIT = config("TEST_ACCOUNT_DATA_LIMIT", cast=int, default=524288000)
TEST_ACCOUNT_DURATION_DAY_LIMIT = config(
    "TEST_ACCOUNT_DURATION_DAY_LIMIT", cast=int, default=3
)
TEST_ACCOUNT_HOST_ZONE_ID = config("TEST_ACCOUNT_HOST_ZONE_ID", cast=int, default=1)

TEST_SERVICE_ID = config("TEST_SERVICE_ID", cast=int, default=0)

JWT_ACCESS_TOKEN_EXPIRE_MINUTES = config(
    "JWT_ACCESS_TOKEN_EXPIRE_MINUTES", cast=int, default=1440
)

# USERNAME: PASSWORD
SUDOERS = {
    config("SUDO_USERNAME", default="admin"): config("SUDO_PASSWORD", default="admin")
}

SUBSCRIPTION_BASE_URL = config(
    "SUBSCRIPTION_BASE_URL", default="https://localhost:8000/api/sub"
)

AVAILABLE_SERVICES = config("AVAILABLE_SERVICES", default="").split(",")

X_UI_REQUEST_TIMEOUT = config("X_UI_REQUEST_TIMEOUT", cast=int, default=20)

XUI_DB_PATH = config("XUI_DB_URL", default="./x-ui.db")
OLD_BOT_DB_PATH = config("OLD_BOT_DB_PATH", default="./v2raybot.sqlite3")

ENABLE_SYNC_ACCOUNTS = config("ENABLE_SYNC_ACCOUNTS", cast=bool, default=False)
ENABLE_REMOVE_DISABLED_ACCOUNTS = config(
    "ENABLE_REMOVE_DISABLED_ACCOUNTS", cast=bool, default=False
)
REMOVE_DISABLED_ACCOUNTS_LAST_DAYS = config(
    "REMOVE_DISABLED_ACCOUNTS_LAST_DAYS", cast=int, default=7
)
REMOVE_UNUSED_TEST_ACCOUNTS_LAST_DAYS = config(
    "REMOVE_UNUSED_TEST_ACCOUNTS_LAST_DAYS", cast=int, default=1
)
REMOVE_DISABLED_ACCOUNTS_JOB_INTERVAL = config(
    "REMOVE_DISABLED_ACCOUNTS_JOB_INTERVAL", cast=int, default=86400
)

ENABLE_NOTIFICATION_SEND_PENDING_JOBS = config(
    "ENABLE_NOTIFICATION_SEND_PENDING_JOBS", cast=bool, default=False
)
ENABLE_NOTIFICATION_JOBS = config("ENABLE_NOTIFICATION_JOBS", cast=bool, default=False)
REVIEW_ACCOUNTS_INTERVAL = config("REVIEW_ACCOUNTS_INTERVAL", cast=int, default=60)
SEND_PENDING_NOTIFICATION_INTERVAL = config(
    "SEND_PENDING_NOTIFICATION_INTERVAL", cast=int, default=60
)

SEND_PENDING_NOTIFICATION_LIMIT = config(
    "SEND_PENDING_NOTIFICATION_LIMIT", cast=int, default=60
)

USED_TRAFFIC_NOTIFICATION_INTERVAL = config(
    "USED_TRAFFIC_NOTIFICATION_INTERVAL", cast=int, default=3600
)
EXPIRE_TIME_NOTIFICATION_INTERVAL = config(
    "EXPIRE_TIME_NOTIFICATION_INTERVAL", cast=int, default=10800
)
SYNC_ACCOUNTS_INTERVAL = config("SYNC_ACCOUNTS_INTERVAL", cast=int, default=60)
SYNC_ACCOUNTS_TRAFFIC_INTERVAL = config(
    "SYNC_ACCOUNTS_TRAFFIC_INTERVAL", cast=int, default=3600
)
GLOBAL_TRAFFIC_RATIO = config("GLOBAL_TRAFFIC_RATIO", cast=float, default=1.0)

ENABLE_ORDER_JOBS = config("ENABLE_ORDER_JOBS", cast=bool, default=False)

PROCESS_PAID_ORDERS_INTERVAL = config(
    "PROCESS_PAID_ORDERS_INTERVAL", cast=int, default=60
)

CLUB_SCORE_PRICE = config("CLUB_SCORE_PRICE", cast=int, default=1000)

REFERRAL_SCORE_0_TO_30 = config("REFERRAL_SCORE_0_TO_30", cast=int, default=5)
REFERRAL_SCORE_30_TO_80 = config("REFERRAL_SCORE_30_TO_80", cast=int, default=15)
REFERRAL_SCORE_80_TO_1000 = config("REFERRAL_SCORE_80_TO_1000", cast=int, default=25)

REFERRAL_ORDER_SCORE_PERCENT = config(
    "REFERRAL_ORDER_SCORE_PERCENT", cast=int, default=5
)

CLUB_CAMPAIGN_RUN_CRON = config("CLUB_CAMPAIGN_RUN_CRON", cast=str, default="0 * * * *")

WEB_APP_URL = config("WEB_APP_URL", cast=str, default="")
