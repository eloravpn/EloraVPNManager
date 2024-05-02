from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

import src.monitoring.service as monitoring_result_service
from src.admins.schemas import Admin
from src.database import get_db
from src.monitoring.schemas import MonitoringResultResponse, MonitoringResultCreate

router = APIRouter()


@router.post("/monitoring-results/", response_model=MonitoringResultResponse)
def add_inbound_config(
    monitoring_result: MonitoringResultCreate,
    db: Session = Depends(get_db),
    admin: Admin = Depends(Admin.get_current),
):

    try:
        db_monitoring_result = monitoring_result_service.create_monitoring_result(
            db=db, monitoring_result=monitoring_result
        )
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Monitoring Result already exists")

    return db_monitoring_result
