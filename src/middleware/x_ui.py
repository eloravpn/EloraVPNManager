import json

import requests

from src import logger
from src.hosts.schemas import HostType, HostResponse


class XUI:
    def __init__(self, host: HostResponse):
        if host.type is HostType.x_ui_sanaei:
            self.api = MHSANAEI(host=host)
        elif host.type is HostType.x_ui_kafka:
            self.api = FRANZKAFKAYU(host=host)


class MHSANAEI:
    def __init__(self, host: HostResponse):
        logger.debug("Init Sanaei X-UI")
        self._host: HostResponse = host

        self._base_api_url = self._generate_base_url(api_path=host.api_path)
        self._login_cookies = self._get_login_cookie()

    def _generate_base_url(self, ssl: bool = False, api_path: str = ""):
        return "%s://%s:%s%s" % (
            "https" if ssl else "http",
            self._host.ip,
            self._host.port,
            api_path,
        )
        logger.debug("Base URL is: " + base_api_url)

    def _get_login_cookie(self):
        login_url = self._generate_base_url() + "/login"
        payload = {"username": self._host.username, "password": self._host.password}
        logger.debug("Try login with url: " + login_url)
        req = requests.request("POST", login_url, data=payload, verify=False)
        return req.cookies

    def get_client_stat(self, email: str):
        url = f"{self._base_api_url}/inbounds/getClientTraffics/{email}"
        client_stat = requests.get(url, cookies=self._login_cookies, verify=False)
        logger.debug(f"Status code: {client_stat.status_code} for client {email}")

        if client_stat.status_code != 200:
            logger.info("Error in fetch api")
            return None
        else:
            logger.debug(f"Account info: {client_stat.text}")
            data = client_stat.json()
            obj = data["obj"]
            if obj is None:
                logger.info(f"Account does not exist with email {email}")
                return None
            else:
                return obj

    def reset_client_traffic(self, inbound_id: int, email: str):
        headers = {"Content-type": "application/json", "Accept": "text/plain"}

        url = f"{self._base_api_url}/inbounds/{inbound_id}/resetClientTraffic/{email}"

        logger.debug(f"Final url for reset client traffic is: {url}")

        response = requests.post(
            url, cookies=self._login_cookies, verify=False, headers=headers
        )
        data = response.json()
        logger.debug(f"Response code: {response.status_code}")
        logger.debug(f"Response text: {response.text}")

        if response.status_code == 200 and data["success"] == True:
            return True
        else:
            return False

    def delete_client(self, inbound_id: int, uuid: str):
        headers = {"Content-type": "application/json", "Accept": "text/plain"}

        url = f"{self._base_api_url}/inbounds/{inbound_id}/delClient/{uuid}"

        logger.debug(f"Final url for delete client is: {url}")

        response = requests.post(
            url, cookies=self._login_cookies, verify=False, headers=headers
        )
        data = response.json()
        logger.info(f"Response code: {response.status_code}")
        logger.info(f"Response text: {response.text}")

        if response.status_code == 200 and data["success"] == True:
            return True
        else:
            return False

    def add_client(
        self,
        inbound_id: int,
        email: str,
        uuid: str,
        data_limit: int = 0,
        expire_time: int = 0,
        ip_limit: int = 0,
        flow: str = "",
        enable: bool = True,
    ):
        headers = {"Content-type": "application/json", "Accept": "text/plain"}

        url = f"{self._base_api_url}/inbounds/addClient"

        logger.debug(f"Final url fro add client is: {url}")

        payload_add_client = MHSANAEI.get_client_payload(
            data_limit,
            email,
            enable,
            expire_time,
            inbound_id,
            uuid,
            ip_limit=ip_limit,
            flow=flow,
        )

        logger.debug(f"Final payload to add client is: {payload_add_client}")

        response = requests.post(
            url,
            cookies=self._login_cookies,
            data=payload_add_client,
            verify=False,
            headers=headers,
        )
        data = response.json()

        logger.debug(f"Response code: {response.status_code}")
        logger.debug(f"Response text: {response.text}")

        if response.status_code == 200 and data["success"] == True:
            return True
        else:
            return False

    def update_client(
        self,
        inbound_id: int,
        email: str,
        uuid: str,
        data_limit: int = 0,
        expire_time: int = 0,
        enable: bool = True,
    ):
        headers = {"Content-type": "application/json", "Accept": "text/plain"}

        url = f"{self._base_api_url}/inbounds/updateClient/{uuid}"

        logger.debug(f"Final url for update client is: {url}")

        payload_add_client = MHSANAEI.get_client_payload(
            data_limit, email, enable, expire_time, inbound_id, uuid
        )

        logger.debug(f"Final payload to update is: {payload_add_client}")

        response = requests.post(
            url,
            cookies=self._login_cookies,
            data=payload_add_client,
            verify=False,
            headers=headers,
        )
        data = response.json()

        logger.debug(f"Response code: {response.status_code}")
        logger.debug(f"Response text: {response.text}")

        if response.status_code == 200 and data["success"] == True:
            return True
        else:
            return False

    @staticmethod
    def get_client_payload(
        data_limit: int,
        email: str,
        enable: bool,
        expire_time: int,
        inbound_id: int,
        uuid: str,
        ip_limit: int = 0,
        flow: str = "",
    ) -> object:
        """
        :param data_limit Data Limit
        :rtype: object
        """
        client = {
            "id": uuid,
            "flow": flow,
            "alterId": 0,
            "email": email,
            "limitIp": ip_limit,
            "totalGB": data_limit,
            "expiryTime": expire_time,
            "enable": enable,
            "tgId": "",
            "subId": "",
        }
        clients = [client]
        clients_object = {"clients": clients}
        payload_add_client = json.dumps(
            {"id": inbound_id, "settings": json.dumps(clients_object)}
        )
        return payload_add_client


class FRANZKAFKAYU:
    def __init__(self):
        logger.info("init Kafka")

    def reset_traffic(self):
        logger.info(f"Traffic reseted {self.__class__}")
