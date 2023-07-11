import json
from datetime import datetime

import requests
from requests.cookies import RequestsCookieJar

from src import scheduler, logger
from src.accounts.service import get_accounts
from src.database import GetDB
from src.hosts.service import get_host
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


def get_client_stat(base_api_url, login_cookies: RequestsCookieJar, email: str):
    url = f'{base_api_url}/inbounds/getClientTraffics/{email}'
    client_stat = requests.get(url,
                               cookies=login_cookies, verify=False)
    logger(f"Status code: {client_stat.status_code} for client {email}")


def get_account_email_prefix(host_id: int, inbound_key: int):
    return "%s_%s_" % (host_id, inbound_key)


def sync_accounts():
    with GetDB() as db:
        # for account in get_accounts(db, return_with_count=False):
        #     logger.info(account.uuid)
        #     logger.info(account.email)

        now = datetime.utcnow().timestamp()
        print('Start syncing accounts in inbounds ' + str(datetime.now()))

        inbounds, count = get_inbounds(db=db)
        for inbound in inbounds:
            logger.info(f"Inbound Remark: {inbound.remark}")
            logger.info(f"Inbound host ID: {inbound.host_id}")

            host = get_host(db, inbound.host_id)
            logger.info("Host name: " + host.name)

            host_ip = host.ip
            host_port = host.port
            user_name = host.username
            password = host.password

            base_login_api_url = generate_base_url(host_ip, host_port, "", False)

            loging_cookies = get_login_cookie(base_login_api_url, user_name, password)

            logger.info("Login Cookies is " + str(loging_cookies))

            account_email_prefix = get_account_email_prefix(host.id, inbound.key)
            logger.info("Account email prefix: " + account_email_prefix)

            for account in get_accounts(db, return_with_count=False):
                logger.info(f"Account uuid: {account.uuid}")
                logger.info(f"Account email: {account.email}")
                logger.info(account.email)


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

    pass


# scheduler.add_job(review_accounts, 'interval', seconds=5)
scheduler.add_job(sync_accounts, 'interval', seconds=5)
