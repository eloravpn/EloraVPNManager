import logging

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_responses import custom_openapi

from config import DOCS
from src.admins.router import router as admin_router
from src.database import Base, engine
from src.hosts.router import router as host_router
from src.inbounds.router import router as inbound_router

app = FastAPI(
    docs_url='/docs' if DOCS else None,
    redoc_url='/redoc' if DOCS else None
)
app.openapi = custom_openapi(app)
scheduler = BackgroundScheduler({'apscheduler.job_defaults.max_instances': 5}, timezone='UTC')
logger = logging.getLogger('uvicorn.error')
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(host_router, prefix="/api", tags=["Host"])
app.include_router(admin_router, prefix="/api", tags=["Admin"])
app.include_router(inbound_router, prefix="/api", tags=["Inbound"])


# from src import dashboard, jobs, hosts, telegram  # noqa

# from src import hosts, admins


@app.on_event("startup")
def on_startup():
    scheduler.start()
    print('OK')
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)



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
