import json
from datetime import datetime

import requests

from src import scheduler, logger
from src.accounts.service import get_accounts
from src.database import GetDB
from src.inbounds.service import get_inbounds


# from src.users.service import get_users


def generate_base_url(host_address: str, host_port: int, api_path: str, ssl: bool):
    return '%s://%s:%s%s' % ("https" if ssl else "http", host_address, host_port, api_path)
    logger.info("Base URL is: " + base_api_url)


def get_login_cookie(base_api_url: str, username: str, password: str):
    login_url = base_api_url + "/login"
    payload = {
        "username": username,
        "password": password
    }
    logger.info("Try login with url: " + login_url)
    req = requests.request("POST", login_url, data=payload, verify=False)
    return req.cookies


def review_accounts():
    print('Start Review accounts ' + str(datetime.now()))
    host_ip = ""
    host_port = 1234
    user_name = "admin"
    password = "admin"

    base_log_api_url = generate_base_url(host_ip, host_port, "", False)
    base_api_url = generate_base_url(host_ip, host_port, "/panel/API", False)

    loging_cookies = get_login_cookie(base_log_api_url, user_name, password)

    logger.info("Login Cookies is " + str(loging_cookies))

    inbound_list = requests.get(base_api_url + '/inbounds/list',
                                cookies=loging_cookies, verify=False)
    logger.info(inbound_list.text)

    data = inbound_list.json()

    logger.info(len(data["obj"]))

    settings = data["obj"][2]["settings"]
    remark = data["obj"][0]["remark"]
    # print(settings)
    settingsObj = json.loads(str(settings))
    logger.info(remark)
    # print(settingsObj["clients"][0]["id"])

    for client in settingsObj["clients"]:
        logger.info(client["id"])
        client_state = requests.get(base_api_url + '/inbounds/getClientTraffics/' + client["email"],
                                    cookies=loging_cookies, verify=False)
        logger.info(client_state.text)

    now = datetime.utcnow().timestamp()
    with GetDB() as db:
        for account in get_accounts(db, return_with_count=False):
            logger.info(account.uuid)
            logger.info(account.email)

        inbounds, count = get_inbounds(db=db)
        for inbound in inbounds:
            logger.info(inbound.host_id)

    pass


scheduler.add_job(review_accounts, 'interval', seconds=5)
