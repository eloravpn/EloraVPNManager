import base64

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette.responses import PlainTextResponse

import src.accounts.service as account_service
from src.database import get_db
from src.inbound_configs.service import get_inbound_configs
from src.utils import xray

router = APIRouter()


# logger = logging.getLogger('uvicorn.error')


@router.get("/sub/{uuid}", tags=["Subscription"], response_class=PlainTextResponse)
def sub(
    uuid: str, size: int = -1, develop: bool = False, db: Session = Depends(get_db)
):
    db_account = account_service.get_account_by_uuid(db=db, uuid=uuid)

    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")

    inbound_configs, count = get_inbound_configs(
        db=db, host_zone_id=db_account.host_zone_id
    )

    rows = []

    for inbound_config in inbound_configs:
        if (
            inbound_config.enable
            and inbound_config.inbound.enable
            and (inbound_config.develop is not True or develop is True)
        ):
            link = xray.generate_vless_config(
                address=inbound_config.address,
                network_type=inbound_config.network.value,
                port=inbound_config.port,
                uuid=uuid,
                host=inbound_config.host,
                sni=inbound_config.sni,
                fp=inbound_config.finger_print.value,
                path=inbound_config.path,
                security=inbound_config.security.value,
                sid=inbound_config.sid,
                pbk=inbound_config.pbk,
                spx=inbound_config.spx,
                remark=inbound_config.remark,
            )
            rows.append(link)

    text = "\n".join(rows) + "\n"
    html = base64.b64encode(text.encode("utf-8"))

    return html
