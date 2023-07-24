from datetime import datetime

from src import scheduler, logger
from src.accounts.models import Account
from src.accounts.service import get_accounts, update_account_used_traffic, update_account_status, \
    create_account_used_traffic
from src.database import GetDB
from src.hosts.schemas import HostResponse
from src.hosts.service import get_host
from src.inbounds.service import get_inbounds
from src.middleware.x_ui import XUI


# from src.users.service import get_users


# def generate_base_url(host_address: str, host_port: int, api_path: str, ssl: bool):
#     return '%s://%s:%s%s' % ("https" if ssl else "http", host_address, host_port, api_path)
#     logger.info("Base URL is: " + base_api_url)
#
#
# def get_login_cookie(base_api_url: str, username: str, password: str):
#     login_url = base_api_url + "/login"
#     payload = {
#         "username": username,
#         "password": password
#     }
#     logger.info("Try login with url: " + login_url)
#     req = requests.request("POST", login_url, data=payload, verify=False)
#     return req.cookies
#
#
# def get_client_stat(base_api_url, login_cookies: RequestsCookieJar, email: str):
#     url = f'{base_api_url}/inbounds/getClientTraffics/{email}'
#     client_stat = requests.get(url,
#                                cookies=login_cookies, verify=False)
#     logger.info(f"Status code: {client_stat.status_code} for client {email}")
#     if client_stat.status_code != 200:
#         logger.info("Error in fetch api")
#         return None
#     else:
#         logger.info(f"Account info: {client_stat.text}")
#         data = client_stat.json()
#         obj = data['obj']
#         if obj is None:
#             logger.info(f"Account does not exist with email {email}")
#             return None
#         else:
#             return obj
#
#
# def reset_client_traffic(base_api_url, login_cookies: RequestsCookieJar, inbound_id: int,
#                          email: str):
#     headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
#
#     url = f'{base_api_url}/inbounds/{inbound_id}/resetClientTraffic/{email}'
#
#     logger.info(f"Final url fro reset client traffic is: {url}")
#
#     response = requests.post(
#         url,
#         cookies=login_cookies, verify=False, headers=headers)
#     data = response.json()
#     logger.info(f"Response code: {response.status_code}")
#     logger.info(f"Response text: {response.text}")
#
#     if response.status_code == 200 and data["success"] == True:
#         return True
#     else:
#         return False
#
#
# def add_client(base_api_url, login_cookies: RequestsCookieJar, inbound_id: int,
#                email: str, uuid: str, data_limit: int = 0, expire_time: int = 0,
#                enable: bool = True):
#     headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
#
#     url = f'{base_api_url}/inbounds/addClient'
#
#     logger.info(f"Final url fro add client is: {url}")
#
#     payload_add_client = get_client_payload(data_limit, email, enable, expire_time, inbound_id, uuid)
#
#     logger.info(f"Final payload to add client is: {payload_add_client}")
#
#     response = requests.post(
#         url,
#         cookies=login_cookies, data=payload_add_client, verify=False, headers=headers)
#     data = response.json()
#
#     logger.info(f"Response code: {response.status_code}")
#     logger.info(f"Response text: {response.text}")
#
#     if response.status_code == 200 and data["success"] == True:
#         return True
#     else:
#         return False
#
#
# def update_client(base_api_url, login_cookies: RequestsCookieJar, inbound_id: int,
#                   email: str, uuid: str, data_limit: int = 0, expire_time: int = 0,
#                   enable: bool = True):
#     headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
#
#     url = f'{base_api_url}/inbounds/updateClient/{uuid}'
#
#     logger.info(f"Final url for update client is: {url}")
#
#     payload_add_client = get_client_payload(data_limit, email, enable, expire_time, inbound_id, uuid)
#
#     logger.info(f"Final payload to update is: {payload_add_client}")
#
#     response = requests.post(
#         url,
#         cookies=login_cookies, data=payload_add_client, verify=False, headers=headers)
#     data = response.json()
#
#     logger.info(f"Response code: {response.status_code}")
#     logger.info(f"Response text: {response.text}")
#
#     if response.status_code == 200 and data["success"] == True:
#         return True
#     else:
#         return False
#
#
# def get_client_payload(data_limit, email, enable, expire_time, inbound_id, uuid):
#     client = {
#         "id": uuid,
#         "alterId": 0,
#         "email": email,
#         "limitIp": 0,
#         "totalGB": data_limit,
#         "expiryTime": expire_time,
#         "enable": enable,
#         "tgId": "",
#         "subId": ""
#     }
#     print(client)
#     clients = []
#     clients.append(client)
#     clients_object = {
#         "clients": clients
#     }
#     payload_add_client = json.dumps({
#         "id": inbound_id,
#         "settings": json.dumps(clients_object)
#     })
#     return payload_add_client
#

def get_account_email_prefix(host_id: int, inbound_key: int, email: str):
    return "%s_%s_%s" % (host_id, inbound_key, email)


def update_client_in_all_inbounds(db, db_account: Account, enable: bool = False):
    inbounds, count = get_inbounds(db=db)
    for inbound in inbounds:
        logger.info(f"Inbound Remark: {inbound.remark}")
        logger.info(f"Inbound host ID: {inbound.host_id}")

        if not inbound.enable:
            logger.info("Skip this inbound because is disabled.")
            continue

        host = get_host(db, inbound.host_id)
        xui = XUI(host=HostResponse.from_orm(host))

        logger.info("Host name: " + host.name)

        account_unique_email = get_account_email_prefix(host.id, inbound.key, db_account.email)

        client_stat = xui.api.get_client_stat(email=account_unique_email)

        if client_stat is not None:
            # if client_stat["enable"] == enable:
            #     logger.info("This client is synced with account!")
            # else:
            xui.api.update_client(inbound_id=inbound.key, email=account_unique_email,
                                  uuid=db_account.uuid, enable=enable)

        else:
            logger.info(f"Client does not exist in this inbound yet")


def sync_accounts():
    with GetDB() as db:

        print('Start syncing accounts in all inbounds ' + str(datetime.now()))

        inbounds, count = get_inbounds(db=db)
        for inbound in inbounds:
            logger.info(f"Inbound Remark: {inbound.remark}")
            logger.info(f"Inbound host ID: {inbound.host_id}")

            host = get_host(db, inbound.host_id)

            xui = XUI(host=HostResponse.from_orm(host))

            logger.info("Host name: " + host.name)

            for account in get_accounts(db, return_with_count=False):
                # account_expire_time = account.expired_at.timestamp() * 1000
                logger.info(f"Account uuid: {account.uuid}")
                logger.info(f"Account email: {account.email}")
                logger.info(f"Account Expire time: {account.expired_at}")
                logger.info(f"Account Status: {account.enable}")

                if not account.enable:
                    logger.info("Account is disable, skipped to add!")

                account_unique_email = get_account_email_prefix(host.id, inbound.key, account.email)

                client_stat = xui.api.get_client_stat(email=account_unique_email)
                if client_stat is not None:
                    total_usage = int(client_stat['up']) + int(client_stat['down'])
                    logger.info(f"Client Upload: {client_stat['up']}")
                    logger.info(f"Client Download: {client_stat['down']}")
                    logger.info(f"Client total usage: {total_usage}")
                    reset = xui.api.reset_client_traffic(inbound_id=inbound.key, email=account_unique_email)
                    if reset and total_usage > 0:
                        create_account_used_traffic(db=db, db_account=account, upload=int(client_stat['up']),
                                                    download=int(client_stat['down']))
                        update_account_used_traffic(db=db, db_account=account,
                                                    used_traffic=total_usage + account.used_traffic)
                        logger.info(
                            f"Traffic updated and reset successfully in {inbound.remark}-{inbound.key} for {account_unique_email}")
                    else:
                        logger.error(f"Could not reset traffic in target inbound {inbound.remark}-{inbound.key}")


                else:
                    logger.info(f"Client does not exist in this inbound yet")
                    logger.info(f"Try to add client in this inbound")

                    xui.api.add_client(inbound_id=inbound.key, email=account_unique_email, uuid=account.uuid)


def review_accounts():
    now = datetime.utcnow().timestamp()
    print('Start Review accounts ' + str(datetime.now()))

    with GetDB() as db:
        for account in get_accounts(db, return_with_count=False):
            account_expire_time = account.expired_at.timestamp()

            logger.info(f"Account uuid: {account.uuid}")
            logger.info(f"Account email: {account.email}")
            logger.info(f"Account Expire time: {account.expired_at}")
            logger.info(f"Account status: {account.enable}")

            if account_expire_time <= now and account.enable:
                logger.info("Account has been expired due to expired time.")
                update_client_in_all_inbounds(db=db, db_account=account, enable=False)
                update_account_status(db=db, db_account=account, enable=False)


            elif account.used_traffic >= account.data_limit and account.enable:
                logger.info("Account has been expired due to exceeded Data limit usage.")
                update_client_in_all_inbounds(db=db, db_account=account, enable=False)
                update_account_status(db=db, db_account=account, enable=False)


def sync_accounts_status():
    now = datetime.utcnow().timestamp()
    logger.info('Start Sync accounts status' + str(datetime.now()))

    with GetDB() as db:
        for account in get_accounts(db, return_with_count=False):
            if not account.expired_at:
                logger.error("No expire time")
            else:
                account_expire_time = account.expired_at.timestamp()

                logger.info(f"Account uuid: {account.uuid}")
                logger.info(f"Account email: {account.email}")
                logger.info(f"Account Expire time: {account.expired_at}")
                logger.info(f"Account status: {account.enable}")

                if account.enable:
                    update_client_in_all_inbounds(db=db, db_account=account, enable=True)
                    logger.info(f"Account with email {account.email} enable successfully")

                else:
                    update_client_in_all_inbounds(db=db, db_account=account, enable=False)
                    logger.info(f"Account with email {account.email} disable successfully")


# TODO: remove this func for prod
# def temp_review_accounts():
#     print('Start Review accounts ' + str(datetime.now()))
#     host_ip = ""
#     host_port = 1234
#     user_name = "admin"
#     password = "admin"
#
#     base_log_api_url = generate_base_url(host_ip, host_port, "", False)
#     base_api_url = generate_base_url(host_ip, host_port, "/panel/API", False)
#
#     loging_cookies = get_login_cookie(base_log_api_url, user_name, password)
#
#     logger.info("Login Cookies is " + str(loging_cookies))
#
#     inbound_list = requests.get(base_api_url + '/inbounds/list',
#                                 cookies=loging_cookies, verify=False)
#     logger.info(inbound_list.text)
#
#     data = inbound_list.json()
#
#     logger.info(len(data["obj"]))
#
#     settings = data["obj"][2]["settings"]
#     remark = data["obj"][0]["remark"]
#     # print(settings)
#     settingsObj = json.loads(str(settings))
#     logger.info(remark)
#     # print(settingsObj["clients"][0]["id"])
#
#     for client in settingsObj["clients"]:
#         logger.info(client["id"])
#         client_state = requests.get(base_api_url + '/inbounds/getClientTraffics/' + client["email"],
#                                     cookies=loging_cookies, verify=False)
#
#         logger.info(client_state.text)
#
#     now = datetime.utcnow().timestamp()
#
#     pass


def run_account_jobs():
    sync_accounts()
    sync_accounts_status()
    review_accounts()


scheduler.add_job(run_account_jobs)

scheduler.add_job(run_account_jobs, trigger='interval', seconds=3600)
