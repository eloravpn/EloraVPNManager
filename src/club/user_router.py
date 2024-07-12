from fastapi import APIRouter
from fastapi import Request

from src import config
from src.utils.tg_webapp import parse_init_data

club_user_router = APIRouter()


@club_user_router.post("/club/profile", tags=["ClubUser"])
def profile(request: Request):
    data = request.json

    init_data = parse_init_data(
        token=config.TELEGRAM_API_TOKEN, raw_init_data=data["initData"]
    )

    print(f"Init Data: {init_data}")

    if init_data is False:
        return False

    query_id = init_data["query_id"]

    return {"status": f"OK {query_id}!"}
