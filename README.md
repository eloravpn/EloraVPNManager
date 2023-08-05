# Elora VPN Manager
A central solution to manage accounts in a Cluster enviroment of VPN Servers

# Screen shots
## Web panel
![image](https://github.com/eloravpn/EloraVPNManager/assets/125687916/b738eba4-1569-40bc-b492-af9cd7cbf4c0)

![image](https://github.com/eloravpn/EloraVPNManager/assets/125687916/5a2e927e-4ff2-4f5b-8c10-e2ce31a2e106)


# Telegram Bot

![image](https://github.com/eloravpn/EloraVPNManager/assets/125687916/71a26896-5275-4b60-bde6-5d803dc2130d)

![image](https://github.com/eloravpn/EloraVPNManager/assets/125687916/ef5748a1-b8f3-445e-98df-a6bc1651666d)


### Supported:
- x-ui

### Features
- Web based panel Manage users and accounts
- Web based panel to manage hosts, inbounds, inbound configs
- Telegram Bot for Users

### How to install
#### Requirements
``python3`` and ``pip3`` installed on your system.

#### Install python dependencies and start backend

`git clone https://github.com/eloravpn/EloraVPNManager.git && cd EloraVPNManager`

*Note: if you want to use `sqlite` as your database, you can comment `psycopg2==2.9.6` line in `requirements.txt`*

`pip install -r requirements.txt && python main.py`

#### Install react dependencies and start front-end

Change the api port and addres in `web/.env` by `REACT_APP_API_BASE_URL`

##### Dev mode

`cd web && yarn install && yarn start`

##### Production mode

`cd web && yarn install && yarn build && serve -s build`



