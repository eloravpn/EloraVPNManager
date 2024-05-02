import logging

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_responses import custom_openapi

from src.subscription.router import router as subscription_router
from src.accounts.router import router as account_router
from src.admins.router import router as admin_router
from src.config import DOCS, DEBUG
from src.database import Base, engine
from src.hosts.router import host_router as host_router
from src.hosts.router import host_zone_router as host_zone_router
from src.inbound_configs.router import router as inbound_config_router
from src.inbounds.router import router as inbound_router
from src.users.router import router as user_router
from src.commerce.router import (
    order_router,
    service_router,
    payment_router,
    transaction_router,
)

from src.notification.router import notification_router
from src.users.schemas import UserResponse

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
app.openapi = custom_openapi(app)
scheduler = BackgroundScheduler(
    {"apscheduler.job_defaults.max_instances": 1}, timezone="UTC"
)
logger = logging.getLogger("uvicorn.default")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# from src import hosts, admins


from src import jobs, telegram  # noqa


@app.on_event("startup")
def on_startup():
    scheduler.start()
    # Base.metadata.drop_all(bind=engine)
    # Base.metadata.create_all(bind=engine)
    logger.info("Application started successfully!")


@app.on_event("shutdown")
def on_shutdown():
    scheduler.shutdown()


# @app.exception_handler(RequestValidationError)
# def validation_exception_handler(request: Request, exc: RequestValidationError):
#     details = {}
#     for error in exc.errors():
#         details[error["loc"][1]] = error["msg"]
#     return JSONResponse(
#         status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
#         content=jsonable_encoder({"detail": details}),
#     )
