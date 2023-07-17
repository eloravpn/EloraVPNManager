import base64

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette.responses import PlainTextResponse

from src.database import get_db
from src.inbound_configs.service import get_inbound_configs
from src.utils import xray

router = APIRouter()


# logger = logging.getLogger('uvicorn.error')

@router.get("/sub/{uuid}", tags=["Subscription"], response_class=PlainTextResponse)
def sub(uuid: str, size: int = -1, db: Session = Depends(get_db)):
    inbound_configs, count = get_inbound_configs(db=db)

    print("count = " + str(count))

    rows = []

    for inbound_config in inbound_configs:
        print(inbound_config.id)
        print(inbound_config.enable)
        if inbound_config.enable is True:
            link = xray.generate_vless_config(address=inbound_config.address, network_type="ws",
                                              port=inbound_config.port, uuid=uuid,
                                              host=inbound_config.host, path=inbound_config.path,
                                              remark=inbound_config.remark)
            print(link)
            rows.append(link)

    text = '\n'.join(rows) + '\n'
    html = base64.b64encode(text.encode('utf-8'))

    print(html)

    print(size)
    return html