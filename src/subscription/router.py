import base64
import socket

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
    uuid: str,
    size: int = -1,
    plain: bool = False,
    resolve: bool = False,
    develop: bool = False,
    address: str = None,
    q: str = None,
    db: Session = Depends(get_db),
):
    db_account = account_service.get_account_by_uuid(db=db, uuid=uuid)

    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")

    inbound_configs, count = get_inbound_configs(
        db=db, host_zone_id=db_account.host_zone_id, q=q
    )

    rows = []

    for inbound_config in inbound_configs:
        if (
            inbound_config.enable
            and inbound_config.inbound.enable
            and inbound_config.inbound.host.enable
            and (inbound_config.develop is not True or develop is True)
        ):

            if address:
                inbound_address = address
            else:
                inbound_address = inbound_config.address

            if resolve:
                inbound_address = _get_ip(inbound_address)
                remark = inbound_config.remark + " " + inbound_config.address
            else:
                remark = inbound_config.remark

            link = xray.generate_vless_config(
                address=inbound_address,
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
                flow=(
                    inbound_config.inbound.flow.value
                    if inbound_config.inbound.flow
                    else None
                ),
                remark=remark,
                alpns=inbound_config.alpns,
            )
            rows.append(link)

    text = "\n".join(rows) + "\n"
    if not plain:
        html = base64.b64encode(text.encode("utf-8"))
    else:
        html = text.encode("utf-8")

    return html


def _get_ip(d):
    """
    This method returns the first IP address string
    that responds as the given domain name
    """
    try:
        return socket.gethostbyname(d)
    except Exception:
        return d
