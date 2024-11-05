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


# Installation Guide

## System Requirements

### Supported Operating Systems
- Ubuntu 20.04 LTS (Focal Fossa)
- Ubuntu 22.04 LTS (Jammy Jellyfish)
- Debian 10 (Buster)
- Debian 11 (Bullseye)

### Minimum Hardware Requirements
- CPU: 1 core
- RAM: 1 GB
- Storage: 10 GB

### Prerequisites
The installation script will automatically install these dependencies, but for reference, the system needs:
- Python 3.9
- PostgreSQL
- systemd
- curl
- Other dependencies will be installed automatically

## Quick Installation

### One-Line Installation
```bash
# Auto-detects your public IP address
curl -fsSL https://raw.githubusercontent.com/eloravpn/EloraVPNManager/main/install.sh | sudo bash
```

### Custom Domain and Port
```bash
curl -fsSL https://raw.githubusercontent.com/eloravpn/EloraVPNManager/main/install.sh | sudo bash -s -- \
  --domain your-domain.com \
  --port 8000
```

### Full Custom Installation
```bash
curl -fsSL https://raw.githubusercontent.com/eloravpn/EloraVPNManager/main/install.sh | sudo bash -s -- \
  --domain your-domain.com \
  --port 8000 \
  --protocol https \
  --db-name custom_db \
  --db-user custom_user \
  --db-pass your_password \
  --jwt-secret your_jwt_secret
```

## Installation Options

| Option | Description | Default |
|--------|-------------|---------|
| `--domain` | Domain name for the application | localhost |
| `--port` | Port number for the application | 8000 |
| `--protocol` | Protocol (http/https) | http |
| `--db-name` | PostgreSQL database name | elora_db |
| `--db-user` | PostgreSQL user name | elora |
| `--db-pass` | PostgreSQL password | Random generated |
| `--jwt-secret` | JWT secret key | Random generated |


### Domain/IP Configuration
- If no domain is specified, the installer will automatically detect and use your server's public IP
- If public IP detection fails, it will fall back to 'localhost'
- You can always specify a custom domain using the `--domain` option
- The detected or specified domain/IP will be used in the configuration for API endpoints

## Post-Installation

### Service Management
```bash
# Check service status
sudo systemctl status elora-vpn

# Start service
sudo systemctl start elora-vpn

# Stop service
sudo systemctl stop elora-vpn

# Restart service
sudo systemctl restart elora-vpn

# View logs
sudo journalctl -u elora-vpn -f
```

### Configuration
The main configuration file is located at:
```bash
/opt/elora-vpn/.env
```

### Default Paths
- Installation Directory: `/opt/elora-vpn`
- Virtual Environment: `/opt/elora-vpn/venv`
- Service File: `/etc/systemd/system/elora-vpn.service`

## Troubleshooting

### Common Issues

1. **Port Already in Use**
```bash
# Check if port is already in use
sudo lsof -i :8000
sudo netstat -tulpn | grep 8000

# Test port accessibility
nc -zv localhost 8000

# Configure firewall for port
sudo ufw allow 8000/tcp
sudo ufw status
```

2. **Database Connection Issues**
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check database logs
sudo tail -f /var/log/postgresql/postgresql-*.log
```

3. **Service Won't Start**
```bash
# Check detailed error messages
sudo journalctl -u elora-vpn -n 50 --no-pager

# Verify Python path
sudo systemctl cat elora-vpn

# Check file permissions
sudo ls -la /opt/elora-vpn
sudo ls -la /opt/elora-vpn/venv/bin/python

# Manual start for debugging
cd /opt/elora-vpn
sudo ./venv/bin/python main.py
```
### Recovery Procedures

#### 1. Database Backup and Restore
```bash
# Backup database
sudo -u postgres pg_dump elora_db > backup.sql

# Restore database
sudo -u postgres psql elora_db < backup.sql
```

#### 2. Configuration Backup
```bash
# Backup configuration
sudo cp /opt/elora-vpn/.env /opt/elora-vpn/.env.backup
sudo cp -r /opt/elora-vpn/static /opt/elora-vpn/static.backup
```

#### 3. Complete Reset
```bash
# Stop service
sudo systemctl stop elora-vpn

# Reset database
sudo -u postgres psql -c "DROP DATABASE elora_db;"
sudo -u postgres psql -c "CREATE DATABASE elora_db OWNER elora;"

# Reinstall application
rm -rf /opt/elora-vpn/*
# Run installation script again...
```

### Debug Mode

To enable debug mode for more detailed logging:
1. Edit `.env` file:
```bash
sudo nano /opt/elora-vpn/.env

# Change these settings:
DEBUG=true
LOG_LEVEL=10
```

2. Restart service:
```bash
sudo systemctl restart elora-vpn
```

3. Monitor debug logs:
```bash
sudo journalctl -u elora-vpn -f
```

### System Information Collection

When reporting issues, include this information:
```bash
# System info
uname -a
lsb_release -a

# Installation info
python3.9 --version
pip list
systemctl status elora-vpn

# Logs
journalctl -u elora-vpn --no-pager -n 100

# Database status
sudo -u postgres psql -d elora_db -c "\dx"
```

### Getting Help
If you encounter any issues:
1. Check the logs using the commands above
2. Verify your system meets the minimum requirements
3. [Open an issue](https://github.com/eloravpn/EloraVPNManager/issues) on GitHub

## Security Notes
- The installation script automatically generates secure random passwords for the database and JWT secret
- All configuration files are created with proper permissions
- The `.env` file contains sensitive information and is readable only by root
- Default database user has limited permissions to only the necessary database

## Updating
To update to the latest version, run the installation script again. It will:
- Backup your existing configuration
- Install the latest version
- Migrate the database
- Restart the service

## Uninstallation
To completely remove the application:
```bash
sudo systemctl stop elora-vpn
sudo systemctl disable elora-vpn
sudo rm -rf /opt/elora-vpn
sudo rm /etc/systemd/system/elora-vpn.service
sudo systemctl daemon-reload
```

To also remove the database:
```bash
sudo -u postgres psql -c "DROP DATABASE elora_db;"
sudo -u postgres psql -c "DROP USER elora;"
```

##### Admin username and password
Default sudoer username and password is `admin`.

The environment varaibles is SUDO_USERNAME and SUDO_PASSWORD

#### The Web Pannel Repository

Follow the Readme in [Elora VPN Manager Panel](https://github.com/eloravpn/EloraVPNManagerPanel)




