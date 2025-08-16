from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import src.hosts.service as service
from src.admins.schemas import Admin
from src.database import get_db
from src.hosts.schemas import (
    HostResponse,
)
from src.inbounds import service as inbounds_service
from src.logger import logger
from src.middleware.x_ui import XUI

middleware_router = APIRouter()


@middleware_router.post(
    "/middleware/hosts/{host_id}/test-connection", tags=["Middleware"]
)
def test_host_connection(
    host_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(Admin.get_current),
):
    db_host = service.get_host(db, host_id=host_id)
    if not db_host:
        raise HTTPException(status_code=404, detail="Host not found")

    try:
        xui = XUI(host=HostResponse.from_orm(db_host))
        return {
            "result": "OK",
            "message": f"Successfully connected to host '{db_host.name}'",
        }
    except Exception as error:
        # Extract specific error information
        error_type = type(error).__name__
        error_message = str(error)

        # Log the full error for debugging
        logger.error(
            f"Failed to connect to host '{db_host.name}' (ID: {host_id}): {error_type}: {error_message}"
        )

        return {
            "result": "ERROR",
            "error_type": error_type,
            "message": error_message,
            "host_name": db_host.name,
            "host_id": host_id,
        }


@middleware_router.post(
    "/middleware/inbounds/{inbound_id}/delete-all-clients", tags=["Middleware"]
)
def test_host_connection(
    inbound_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(Admin.get_current),
):
    try:
        db_inbound = inbounds_service.get_inbound(db, inbound_id)
        db_host = service.get_host(db, db_inbound.host_id)

        xui = XUI(host=HostResponse.from_orm(db_host))

        xui.api.remove_inbound_clients(db_inbound.key)

        return {
            "result": "SUCCESS",
            "message": "All clients has been deleted in this inbound!",
            "host_name": db_host.name,
            "inbound_id": inbound_id,
        }

    except Exception as error:

        error_type = type(error).__name__
        error_message = str(error)

        # Log the full error for debugging
        logger.error(
            f"Failed to connect to host '{db_host.name}' (Inbound ID: {inbound_id}): {error_type}: {error_message}"
        )

        return {
            "result": "ERROR",
            "error_type": error_type,
            "message": error_message,
            "host_name": db_host.name,
            "inbound_id": inbound_id,
        }
