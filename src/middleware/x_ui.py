import json

import requests

from src.logger import logger
from src import config
from src.hosts.schemas import HostType, HostResponse
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


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

        self._base_api_url = self._generate_base_url(
            api_path=host.api_path, ssl=self._host.master
        )
        self._login_cookies = self._get_login_cookie()

    def _generate_base_url(self, ssl: bool = False, api_path: str = ""):
        address = self._host.ip if self._host.domain is None else self._host.domain

        base_url = "%s://%s:%s%s" % (
            "https" if ssl else "http",
            address,
            self._host.port,
            api_path,
        )

        logger.debug(f"Base URL is: {base_url}")

        return base_url

    def _get_login_cookie(self):
        base_login_url = self._base_api_url.replace("/panel/api", "")
        login_url = base_login_url + "/login"
        payload = {"username": self._host.username, "password": self._host.password}
        logger.debug("Try login with url: " + login_url)
        req = requests.request(
            "POST",
            login_url,
            data=payload,
            verify=False,
            timeout=config.X_UI_REQUEST_TIMEOUT,
        )
        logger.debug(f"Login response: {req.text}")
        return req.cookies

    @staticmethod
    def get_account_email_prefix(inbound_key: int, email: str):
        return "%s_%s" % (inbound_key, email)

    @staticmethod
    def get_account_real_email(client_email: str):
        if client_email is None:
            return None

        email_split = client_email.split("_")

        if len(email_split) > 1:
            if client_email.find(config.TEST_ACCOUNT_EMAIL_PREFIX) > 0:
                return config.TEST_ACCOUNT_EMAIL_PREFIX + email_split[-1]
            else:
                return email_split[-1]
        else:
            return None

    def get_client_stat(self, email: str):
        try:
            url = f"{self._base_api_url}/inbounds/getClientTraffics/{email}"
            client_stat = requests.get(
                url,
                cookies=self._login_cookies,
                verify=False,
                timeout=config.X_UI_REQUEST_TIMEOUT,
            )
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
        except Exception as error:
            logger.warn(error)
            return None

    def reset_client_traffic(self, inbound_id: int, email: str):
        headers = {"Content-type": "application/json", "Accept": "text/plain"}

        url = f"{self._base_api_url}/inbounds/{inbound_id}/resetClientTraffic/{email}"

        logger.debug(f"Final url for reset client traffic is: {url}")

        try:
            response = requests.post(
                url,
                cookies=self._login_cookies,
                verify=False,
                headers=headers,
                timeout=config.X_UI_REQUEST_TIMEOUT,
            )
            data = response.json()
            logger.debug(f"Response code: {response.status_code}")
            logger.debug(f"Response text: {response.text}")

            if response.status_code == 200 and data["success"] == True:
                return True
            else:
                return False
        except Exception as error:
            logger.warn(error)
            return False

    def reset_clients_traffic(self, inbound_id: int):
        headers = {"Content-type": "application/json", "Accept": "text/plain"}

        url = f"{self._base_api_url}/inbounds/resetAllClientTraffics/{inbound_id}"

        logger.info(f"Final url for reset client traffic is: {url}")

        try:
            response = requests.post(
                url,
                cookies=self._login_cookies,
                verify=False,
                headers=headers,
                timeout=config.X_UI_REQUEST_TIMEOUT,
            )

            data = response.json()
            logger.debug(f"Response code: {response.status_code}")
            logger.debug(f"Response text: {response.text}")

            if response.status_code == 200 and data["success"] == True:
                return True
            else:
                return False
        except Exception as error:
            logger.warn(error)
            return False

    def delete_client(self, inbound_id: int, uuid: str):

        try:
            headers = {"Content-type": "application/json", "Accept": "text/plain"}

            url = f"{self._base_api_url}/inbounds/{inbound_id}/delClient/{uuid}"

            logger.debug(f"Final url for delete client is: {url}")

            response = requests.post(
                url,
                cookies=self._login_cookies,
                verify=False,
                headers=headers,
                timeout=config.X_UI_REQUEST_TIMEOUT,
            )
            data = response.json()
            logger.info(f"Response code: {response.status_code}")
            logger.info(f"Response text: {response.text}")

            if response.status_code == 200 and data["success"] == True:
                return True
            else:
                return False
        except Exception as error:
            logger.warn(error)
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

        try:
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
                timeout=config.X_UI_REQUEST_TIMEOUT,
            )
            data = response.json()

            logger.debug(f"Response code: {response.status_code}")
            logger.debug(f"Response text: {response.text}")

            if response.status_code == 200 and data["success"] == True:
                return True
            else:
                return False
        except Exception as error:
            logger.warn(error)
            return False

    def update_client(
        self,
        inbound_id: int,
        email: str,
        uuid: str,
        data_limit: int = 0,
        ip_limit: int = 0,
        flow: str = "",
        expire_time: int = 0,
        enable: bool = True,
    ):
        try:
            headers = {"Content-type": "application/json", "Accept": "text/plain"}

            url = f"{self._base_api_url}/inbounds/updateClient/{uuid}"

            logger.debug(f"Final url for update client is: {url}")

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

            logger.debug(f"Final payload to update is: {payload_add_client}")

            response = requests.post(
                url,
                cookies=self._login_cookies,
                data=payload_add_client,
                verify=False,
                headers=headers,
                timeout=config.X_UI_REQUEST_TIMEOUT,
            )
            data = response.json()

            logger.debug(f"Response code: {response.status_code}")
            logger.debug(f"Response text: {response.text}")

            if response.status_code == 200 and data["success"] is True:
                return True
            else:
                return False
        except Exception as error:
            logger.warn(error)
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

    def get_inbound_client_stats(
        self,
        inbound_id: int,
    ):
        try:
            logger.debug(f"Get clients from {self._host.name} inbound {inbound_id}")

            url = f"{self._base_api_url}/inbounds/list"

            response = requests.get(
                url,
                cookies=self._login_cookies,
                verify=False,
                timeout=config.X_UI_REQUEST_TIMEOUT,
            )

            data = response.json()

            remote_inbound_list = data["obj"]

            if remote_inbound_list is not None:
                for remote_inbound in remote_inbound_list:
                    if int(remote_inbound["id"]) == inbound_id:
                        return remote_inbound["clientStats"]

            return None
        except Exception as error:
            logger.warn(error)
            return None

    def remove_inbound_clients(
        self,
        inbound_id: int,
    ):
        remote_inbound_clients = self.get_inbound_clients(inbound_id)

        for client in remote_inbound_clients:
            client_email = client["email"]
            uuid = client["id"]
            enable = client["enable"]
            logger.info(
                f"Try to delete Email: {client_email}, UUID: {uuid}, Enable:{enable}"
            )
            account_email = self.get_account_real_email(client_email)

            if account_email is None:
                logger.warn("This client is not handle with Elora Panel! Skip!")
                continue

            deleted = self.delete_client(inbound_id=inbound_id, uuid=uuid)
            if not deleted:
                logger.error(
                    f"Error in delete account email {client_email} in this inbound!"
                )
            else:
                logger.info(
                    f"Client email {client_email} Successfully deleted in this inbound!"
                )

    def get_inbound_clients(
        self,
        inbound_id: int,
    ):
        try:
            logger.info(f"Get clients from {self._host.name} inbound {inbound_id}")

            url = f"{self._base_api_url}/inbounds/get/{inbound_id}"

            inbound_stat = requests.get(
                url,
                cookies=self._login_cookies,
                verify=False,
                timeout=config.X_UI_REQUEST_TIMEOUT,
            )

            logger.debug(
                f"Status code: {inbound_stat.status_code} for Inbound {inbound_id}"
            )

            data = inbound_stat.json()

            settings = data["obj"]["settings"]

            if settings:
                setting_obj = json.loads(settings)
                clients = setting_obj["clients"]
                return clients
            else:
                return None
        except Exception as error:
            logger.warn(error)
            return None


class FRANZKAFKAYU:
    def __init__(self):
        logger.info("init Kafka")

    def reset_traffic(self):
        logger.info(f"Traffic reseted {self.__class__}")
