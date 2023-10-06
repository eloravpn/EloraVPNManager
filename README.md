# Elora VPN Manager
A central solution to manage accounts in a Cluster enviroment of VPN Servers.

## Overview
By this application you can manage multi x-ui host and multi inbounds.  
all accounts that created in panel, automatically created and managed in all hosts and inbounds.  
you have a telgram bot for users to view thier accounts sub scription url and used traffic.  
a simple order workfllow for new customers are avialable in telgram bot.

### Contact US in Telegram
[Elora VPN](https://t.me/eloravpn)



### Supported:
- [3x-ui](https://github.com/MHSanaei/3x-ui)

### Features
- Web based panel Manage users and accounts
- Web based panel to manage hosts, inbounds, inbound configs
- Telegram Bot for Users


# Screen shots
## Web panel
![2023-10-06_15-49](https://github.com/eloravpn/EloraVPNManagerPanel/assets/125687916/f28fa7d9-d4d6-43d3-8f25-5a0c8a72153d)

![2023-10-06_15-50_1](https://github.com/eloravpn/EloraVPNManagerPanel/assets/125687916/2272cbaf-0793-40c8-9c29-44f4bea55065)

![2023-10-06_15-50](https://github.com/eloravpn/EloraVPNManagerPanel/assets/125687916/98caa4b5-f42c-46bf-b470-075eb2298f00)


# Telegram Bot

![image](https://github.com/eloravpn/EloraVPNManager/assets/125687916/71a26896-5275-4b60-bde6-5d803dc2130d)

![image](https://github.com/eloravpn/EloraVPNManager/assets/125687916/ef5748a1-b8f3-445e-98df-a6bc1651666d)

### How to install
#### Requirements
``python3`` and ``pip3`` installed on your system.

#### Clone the repository

`git clone https://github.com/eloravpn/EloraVPNManager.git && cd EloraVPNManager`

#### Configuration
You can create a `.env` file and override all configurations in `src/config.py`.
also you can use `.env.example` file as an exmaple.

##### Database
Set users name, password and DB name on bellow proprt in `.env` file:
```
SQLALCHEMY_DATABASE_URL="postgresql+psycopg2://postgres:123456@localhost:5432/eloravpn"
```

##### Admin username and password
Default sudoer username and password is `admin`.

The environment varaibles is SUDO_USERNAME and SUDO_PASSWORD

> *We  strongly recomended to use postgresql as your database*

> *Note: if you want to use `sqlite` as your database, you can comment `psycopg2==2.9.6` line in `requirements.txt`*

> For Ubuntu 20 and 22: install `libpq-dev` by `apt install libpq-dev`

`pip3 install -r requirements.txt && alembic upgrade head && python3  main.py`

#### Install Web Pannel

Follow the Readme in [Elora VPN Manager Panel]([https://github.com/MHSanaei/3x-ui](https://github.com/eloravpn/EloraVPNManagerPanel))




