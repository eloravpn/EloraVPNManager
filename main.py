import uvicorn
from src import app
from src.config import (
    DEBUG,
    UVICORN_HOST,
    UVICORN_PORT,
    UVICORN_UDS,
    UVICORN_SSL_CERTFILE,
    UVICORN_SSL_KEYFILE
)

if __name__ == "__main__":
    # Do NOT change workers count for now
    # multi-workers support isn't implemented yet for APScheduler and XRay module

    log_config = uvicorn.config.LOGGING_CONFIG
    log_config["formatters"]["default"][
        "fmt"] = "%(asctime)s - %(levelname)s - %(module)s.%(funcName)s:%(lineno)d - %(message)s"
    try:
        uvicorn.run(
            "main:app",
            host=('127.0.0.1' if DEBUG else UVICORN_HOST),
            port=UVICORN_PORT,
            uds=(None if DEBUG else UVICORN_UDS),
            ssl_certfile=UVICORN_SSL_CERTFILE,
            ssl_keyfile=UVICORN_SSL_KEYFILE,
            workers=1,
            reload=DEBUG,
            use_colors=True,
            log_config=log_config
        )
    except FileNotFoundError:  # to prevent error on removing unix sock
        pass

# src = FastAPI()
#
#
# @src.get("/")
# async def root():
#     return {"message": "Hello World"}
#
#
# @src.get("/hello/{name}")
# async def say_hello(name: str):
#     return {"message": f"Hello {name}"}
