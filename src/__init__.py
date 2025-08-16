import json
import logging
import os
import signal
import sys

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi_responses import custom_openapi

from src.accounts.router import router as account_router
from src.admins.router import router as admin_router
from src.admins.schemas import Admin
from src.club.user_router import club_user_router
from src.commerce.router import (
    order_router,
    service_router,
    payment_router,
    transaction_router,
    payment_account_router,
)
from src.config import DOCS, DEBUG, UVICORN_HOST, UVICORN_PORT
from src.logger import logger
from src.database import Base, engine
from src.hosts.router import host_router as host_router
from src.hosts.router import host_zone_router as host_zone_router
from src.inbound_configs.router import router as inbound_config_router
from src.inbounds.router import router as inbound_router
from src.middleware.router import middleware_router
from src.monitoring.router import router as monitoring_router
from src.notification.router import notification_router
from src.subscription.router import router as subscription_router
from src.users.router import router as user_router
from src.config_setting.router import router as config_setting_router
from src.system.router import router as system_router
from src.users.schemas import UserResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

# logging_config = dict(
#     version=1,
#     formatters={
#         'f': {'format':
#                   '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'}
#     },
#     handlers={
#         'h': {'class': 'logging.StreamHandler',
#               'formatter': 'f',
#               'level': logging.DEBUG}
#     },
#     root={
#         'handlers': ['h'],
#         'level': logging.DEBUG,
#     },
# )
#
# dictConfig(logging_config)


app = FastAPI(
    docs_url="/docs" if DOCS else None,
    redoc_url="/redoc" if DOCS else None,
    debug=DEBUG,
)

scheduler = BackgroundScheduler(
    {"apscheduler.job_defaults.max_instances": 1}, timezone="UTC"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

static_path = os.path.join(os.path.dirname(__file__), "../static")

app.include_router(subscription_router, prefix="/api", tags=["Subscription"])
app.include_router(host_router, prefix="/api", tags=["Host"])
app.include_router(host_zone_router, prefix="/api", tags=["HostZone"])
app.include_router(admin_router, prefix="/api", tags=["Admin"])
app.include_router(user_router, prefix="/api", tags=["User"])
app.include_router(account_router, prefix="/api", tags=["Account"])
app.include_router(inbound_router, prefix="/api", tags=["Inbound"])
app.include_router(inbound_config_router, prefix="/api", tags=["InboundConfig"])
app.include_router(order_router, prefix="/api", tags=["Order"])
app.include_router(service_router, prefix="/api", tags=["Service"])
app.include_router(payment_router, prefix="/api", tags=["Payment"])
app.include_router(transaction_router, prefix="/api", tags=["Transaction"])
app.include_router(notification_router, prefix="/api", tags=["Notification"])
app.include_router(monitoring_router, prefix="/api", tags=["Monitoring"])
app.include_router(club_user_router, prefix="/api", tags=["ClubUser"])
app.include_router(config_setting_router, prefix="/api", tags=["ConfigSettings"])
app.include_router(payment_account_router, prefix="/api", tags=["PaymentAccounts"])

app.include_router(system_router, prefix="/api", tags=["System"])
app.include_router(middleware_router, prefix="/api", tags=["Middleware"])


@app.get("/static/config.json")
async def custom_config(request: Request):
    try:
        config_path = os.path.join(static_path, "config.json")
        if not os.path.exists(config_path):
            raise HTTPException(status_code=404, detail="Config file not found")

        with open(config_path, "r") as f:
            config_data = json.load(f)

        base_url = config.CUSTOM_BASE_URL

        if base_url is None:
            config_data["BASE_URL"] = str(request.base_url) + "api/"
        else:
            config_data["BASE_URL"] = base_url

        return JSONResponse(content=config_data)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid config file format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Mount static files for specific paths
if os.path.exists(static_path) and os.path.isdir(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")


# Custom exception handler for 404 errors
@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        # If path starts with /api, return 404 API error
        if request.url.path.startswith("/api/"):
            return JSONResponse(
                status_code=404, content={"detail": "API endpoint not found"}
            )

        # For all other paths, serve index.html
        index_path = os.path.join(static_path, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)

    return JSONResponse(
        status_code=exc.status_code, content={"detail": str(exc.detail)}
    )


# OpenAPI customization
app.openapi = custom_openapi(app)


# from src import hosts, admins

from src import jobs, telegram  # noqa
from src.club import jobs  # noqa


@app.post(path="/api/restart")
async def restart_server(admin: Admin = Depends(Admin.get_current)):
    try:
        os.kill(os.getpid(), signal.SIGTERM)
        return JSONResponse({"message": "Server restarting..."})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.on_event("startup")
def on_startup():
    scheduler.start()
    logger.info("Application started successfully!")


@app.on_event("shutdown")
def on_shutdown():
    scheduler.shutdown()


# Root path handler
@app.get("/")
async def root():
    index_path = os.path.join(static_path, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    raise HTTPException(status_code=404, detail="Frontend not installed")


# @app.exception_handler(RequestValidationError)
# def validation_exception_handler(request: Request, exc: RequestValidationError):
#     details = {}
#     for error in exc.errors():
#         details[error["loc"][1]] = error["msg"]
#     return JSONResponse(
#         status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
#         content=jsonable_encoder({"detail": details}),
#     )
