# Elora VPN Manager
A central solution to manage accounts in a Cluster enviroment of VPN Servers.

## Overview
By this application you can manage multi x-ui host and multi inbounds.  
all accounts that created in panel, automatically created and managed in all hosts and inbounds.  
you have a telgram bot for users to view thier accounts sub scription url and used traffic.  
a simple order workfllow for new customers are avialable in telgram bot.  



### Supported:
- [3x-ui](https://github.com/MHSanaei/3x-ui)

### Features
- Web based panel Manage users and accounts
- Web based panel to manage hosts, inbounds, inbound configs
- Telegram Bot for Users


# Screen shots
## Web panel
![image](https://github.com/eloravpn/EloraVPNManager/assets/125687916/b738eba4-1569-40bc-b492-af9cd7cbf4c0)

![image](https://github.com/eloravpn/EloraVPNManager/assets/125687916/5a2e927e-4ff2-4f5b-8c10-e2ce31a2e106)


# Telegram Bot

![image](https://github.com/eloravpn/EloraVPNManager/assets/125687916/71a26896-5275-4b60-bde6-5d803dc2130d)

![image](https://github.com/eloravpn/EloraVPNManager/assets/125687916/ef5748a1-b8f3-445e-98df-a6bc1651666d)

### How to install
#### Requirements
``python3`` and ``pip3`` installed on your system.
Also to start web panel you need `node v20.4.0+` and `yarn`

#### Configuration
You can create a `.env` file and override all configurations in `src/config.py`.
also you can use `.env.example` file as an exmaple.

##### Admin username and password
Default sudoer username and password is `admin`.

The environment varaibles is SUDO_USERNAME and SUDO_PASSWORD


> [!NOTE]
> *We  strongly recomended to use postgresql as your database*
#### Install python dependencies and start backend

`git clone https://github.com/eloravpn/EloraVPNManager.git && cd EloraVPNManager`

> [!NOTE]
> *Note: if you want to use `sqlite` as your database, you can comment `psycopg2==2.9.6` line in `requirements.txt`*

`pip install -r requirements.txt && alembic upgrade head && python main.py`

#### Install react dependencies and start front-end

Change the api port and addres in `web/.env` by `REACT_APP_API_BASE_URL`

##### Dev mode

`cd web && yarn install && yarn start`

##### Production mode

`cd web && yarn install && yarn build && serve -s build`



