import ssl
from pathlib import Path
from typing import Optional

import uvicorn
from src import app
from src.logger import logger

from src import config
from src.config import (
    DEBUG,
    UVICORN_HOST,
    UVICORN_PORT,
    UVICORN_UDS,
    UVICORN_SSL_CERTFILE,
    UVICORN_SSL_KEYFILE,
)


def validate_ssl_files() -> tuple[Optional[str], Optional[str]]:
    """
    Validate SSL certificate and key files, supporting both CA-signed and self-signed certificates.
    Returns a tuple of (certfile, keyfile) if valid, or (None, None) if invalid or not configured.
    """
    if not UVICORN_SSL_CERTFILE or not UVICORN_SSL_KEYFILE:
        return None, None

    cert_path = Path(UVICORN_SSL_CERTFILE)
    key_path = Path(UVICORN_SSL_KEYFILE)

    # Check if files exist
    if not cert_path.exists():
        logger.warning(f"SSL certificate file not found: {UVICORN_SSL_CERTFILE}")
        return None, None
    if not key_path.exists():
        logger.warning(f"SSL key file not found: {UVICORN_SSL_KEYFILE}")
        return None, None

    try:
        # Create a context that doesn't validate certificate chain
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        # Try to load the certificate and private key
        ssl_context.load_cert_chain(certfile=str(cert_path), keyfile=str(key_path))

        logger.info(
            "SSL configuration validated successfully (self-signed certificates supported)"
        )
        return str(cert_path), str(key_path)
    except (ssl.SSLError, Exception) as e:
        logger.warning(
            f"Invalid SSL configuration: {str(e)}. Starting server without SSL."
        )
        return None, None


if __name__ == "__main__":
    # Do NOT change workers count for now
    # multi-workers support isn't implemented yet for APScheduler and XRay module

    log_config = uvicorn.config.LOGGING_CONFIG
    log_config["formatters"]["default"][
        "fmt"
    ] = "%(asctime)s - %(levelname)s - %(module)s.%(funcName)s:%(lineno)d - %(message)s"
    log_config["loggers"]["uvicorn"]["level"] = config.LOG_LEVEL

    uds_path = UVICORN_UDS if UVICORN_UDS and len(UVICORN_UDS.strip()) > 0 else None

    # Validate SSL files - will return None, None if invalid
    ssl_cert, ssl_key = validate_ssl_files()

    try:
        uvicorn.run(
            "main:app",
            host=("127.0.0.1" if DEBUG else UVICORN_HOST),
            port=UVICORN_PORT,
            uds=uds_path,
            ssl_certfile=ssl_cert,
            ssl_keyfile=ssl_key,
            forwarded_allow_ips="*",
            workers=1,
            reload=DEBUG,
            use_colors=True,
            log_config=log_config,
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
