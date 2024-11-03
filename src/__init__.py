import logging
import os

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi_responses import custom_openapi

from src.accounts.router import router as account_router
from src.admins.router import router as admin_router
from src.club.user_router import club_user_router
from src.commerce.router import (
    order_router,
    service_router,
    payment_router,
    transaction_router,
)
from src.config import DOCS, DEBUG, UVICORN_HOST, UVICORN_PORT
from src.database import Base, engine
from src.hosts.router import host_router as host_router
from src.hosts.router import host_zone_router as host_zone_router
from src.inbound_configs.router import router as inbound_config_router
from src.inbounds.router import router as inbound_router
from src.monitoring.router import router as monitoring_router
from src.notification.router import notification_router
from src.subscription.router import router as subscription_router
from src.users.router import router as user_router
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

# Mount static files and setup SPA handling
static_path = os.path.join(os.path.dirname(__file__), "../static")

# Ensure the app has static files handling

# Check if static folder exists
if os.path.exists(static_path) and os.path.isdir(static_path):
    # Mount static files if directory exists
    app.mount("/static", StaticFiles(directory=static_path), name="static")


@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    # Don't serve frontend for API routes
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="Not found")

    # Serve index.html for all other routes
    index_path = os.path.join(static_path, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    raise HTTPException(status_code=404, detail="Frontend not installed")


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
app.include_router(monitoring_router, prefix="/api", tags=["Monitoring"])
app.include_router(club_user_router, prefix="/api", tags=["ClubUser"])

# from src import hosts, admins


from src import jobs, telegram  # noqa
from src.club import jobs  # noqa


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
