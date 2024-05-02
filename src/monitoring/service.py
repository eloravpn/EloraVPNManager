from sqlalchemy.orm import Session

from src.monitoring.models import MonitoringResult
from src.monitoring.schemas import MonitoringResultCreate


def create_monitoring_result(
    db: Session,
    monitoring_result: MonitoringResultCreate,
):

    db_monitoring_result = MonitoringResult(
        client_name=monitoring_result.client_name,
        client_ip=monitoring_result.client_ip,
        test_url=monitoring_result.test_url,
        remark=monitoring_result.remark,
        port=monitoring_result.port,
        domain=monitoring_result.domain,
        sni=monitoring_result.sni,
        delay=monitoring_result.delay,
        ping=monitoring_result.ping,
        develop=monitoring_result.develop,
        success=monitoring_result.success,
    )
    db.add(db_monitoring_result)
    db.commit()
    db.refresh(db_monitoring_result)
    return db_monitoring_result
