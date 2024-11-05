#!/bin/bash

# Exit on any error
set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
INSTALL_DIR="/opt/elora-vpn"
ENV="production"
DOMAIN="localhost:8000"
PROTOCOL="http"
SERVICE_NAME="elora-vpn"
PYTHON_MIN_VERSION="3.8"
DB_NAME="elora_db"
DB_USER="elora"
DB_HOST="localhost"
JWT_SECRET=""
USER_NAME="admin"
PASSWORD=""

# Log function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

# Error function
error() {
    echo -e "${RED}[ERROR] $1${NC}" >&2
    exit 1
}

# Warning function
warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}" >&2
}

# Generate random password for database
generate_password() {
    tr -dc 'A-Za-z0-9' </dev/urandom | head -c 16
}

# Generate random string for JWT secret
generate_jwt_secret() {
    tr -dc 'A-Za-z0-9!"#$%&'\''()*+,-./:;<=>?@[\]^_`{|}~' </dev/urandom | head -c 50
}

# Function to install packages non-interactively
apt_install() {
    export DEBIAN_FRONTEND=noninteractive
    apt-get install -y -q -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" "$@"
}

# Function to download and extract latest release
download_latest_release() {
    log "Downloading latest release..."

    # Create temporary directory
    local temp_dir=$(mktemp -d)
    cd "$temp_dir"

    # Download latest release information
    log "Fetching latest release information..."
    LATEST_RELEASE=$(curl -s https://api.github.com/repos/eloravpn/EloraVPNManager/releases/latest)
    DOWNLOAD_URL=$(echo $LATEST_RELEASE | jq -r '.assets[0].browser_download_url')
    VERSION=$(echo $LATEST_RELEASE | jq -r '.tag_name')

    if [ -z "$DOWNLOAD_URL" ] || [ "$DOWNLOAD_URL" = "null" ]; then
        error "Could not find release download URL"
    fi

    log "Downloading version ${VERSION}..."
    curl -L -o release.zip "$DOWNLOAD_URL" || error "Failed to download release"

    # Extract files
    log "Extracting files..."
    unzip -q release.zip -d "$INSTALL_DIR" || error "Failed to extract files"

    # Verify required files
    log "Verifying installation files..."
    required_files=("requirements.txt" "main.py" "alembic.ini")
    for file in "${required_files[@]}"; do
        if [ ! -f "${INSTALL_DIR}/${file}" ]; then
            error "Required file ${file} not found after extraction"
        fi
    done

    # Clean up
    cd - > /dev/null
    rm -rf "$temp_dir"

    log "Successfully downloaded and extracted version ${VERSION}"
    log "All required files verified"
}

# Check if required tools are available
check_download_tools() {
    log "Checking required tools..."
    local required_tools=("curl" "jq" "unzip")

    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            log "Installing ${tool}..."
            apt_install "$tool" || error "Failed to install ${tool}"
        fi
    done
}

# Update environment configuration
update_env() {
    log "Updating .env configuration..."
    local env_file="$INSTALL_DIR/.env"

    # Generate JWT secret if not provided
    JWT_SECRET=${JWT_SECRET:-$(generate_jwt_secret)}
    PASSWORD=${PASSWORD:-$(generate_password)}

    # Create .env file
    cat > "$env_file" << EOL
SUDO_USERNAME = "${USER_NAME}"
SUDO_PASSWORD = "${PASSWORD}"

# Server Configuration
DEBUG=false
DOCS=false
UVICORN_HOST=0.0.0.0
UVICORN_PORT=${PORT}
UVICORN_UDS=

#SSL Configuration
UVICORN_SSL_CERTFILE=
UVICORN_SSL_KEYFILE=

# Database Configuration
SQLALCHEMY_DATABASE_URL="postgresql+psycopg2://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:5432/${DB_NAME}"

# JWT Settings
JWT_SECRET_KEY=${JWT_SECRET}
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Telegram Settings
TELEGRAM_PAYMENT_API_TOKEN=
BOT_USER_NAME=
TELEGRAM_API_TOKEN=
#TELEGRAM_ADMIN_ID=
TELEGRAM_ADMIN_USER_NAME=
TELEGRAM_CHANNEL=
SUBSCRIPTION_BASE_URL=${PROTOCOL}://${DOMAIN}:${PORT}/api/

# Other Settings
ENABLE_NOTIFICATION_SEND_PENDING_JOBS=True
ENABLE_SYNC_ACCOUNTS=True
ENABLE_NOTIFICATION_JOBS= True

EOL

    # Set proper permissions
    chmod 600 "$env_file"
    log "Environment configuration updated successfully"
}


# Function to setup and activate virtual environment
setup_virtualenv() {
    log "Setting up Python virtual environment..."

    # Create venv if it doesn't exist
    if [ ! -d "${INSTALL_DIR}/venv" ]; then
        python3 -m venv "${INSTALL_DIR}/venv" || error "Failed to create virtual environment"
    fi

    # Activate virtual environment
    source "${INSTALL_DIR}/venv/bin/activate" || error "Failed to activate virtual environment"

    # Upgrade pip in virtual environment
    log "Upgrading pip in virtual environment..."
    "${INSTALL_DIR}/venv/bin/pip" install --upgrade pip || error "Failed to upgrade pip"
}

# Function to check and install system dependencies
check_dependencies() {
    log "Checking and installing dependencies..."

    # Update package list
    apt-get update -qq || error "Failed to update package list"

    # List of required packages
    local packages=(
        "python3"
        "python3-pip"
        "python3-venv"
        "python3-dev"  # Required for some Python packages
        "jq"
        "unzip"
        "wget"
        "systemd"
        "postgresql"  # PostgreSQL itself
        "postgresql-contrib"
        "libpq-dev"  # Required for psycopg2
        "gcc"  # Required for compiling
        "python3-wheel"  # For building wheels
        "build-essential"  # Build tools
    )


    # Ensure PostgreSQL is installed
    if ! command -v psql &> /dev/null; then
        log "Installing PostgreSQL..."
        apt_install postgresql postgresql-contrib
    fi


    # Check and install missing packages
    for pkg in "${packages[@]}"; do
        if ! dpkg -l | grep -q "^ii  $pkg "; then
            log "Installing $pkg..."
            apt_install "$pkg" || error "Failed to install $pkg"
        fi
    done
}

# Check if PostgreSQL is running and accessible
check_postgresql() {
    log "Checking PostgreSQL status..."
    if ! systemctl is-active --quiet postgresql; then
        log "Starting PostgreSQL..."
        systemctl start postgresql
        systemctl enable postgresql
    fi

    # Wait for PostgreSQL to be ready
    for i in {1..30}; do
        if su - postgres -c "psql -l" &>/dev/null; then
            log "PostgreSQL is running and accessible"
            return 0
        fi
        sleep 1
    done
    error "PostgreSQL is not responding after 30 seconds"
}

# Setup PostgreSQL database
setup_database() {
    log "Setting up PostgreSQL database..."

    # Generate random password if not set
    DB_PASSWORD=${DB_PASSWORD:-$(generate_password)}
    DB_NAME=${DB_NAME:-"elora_db"}
    DB_USER=${DB_USER:-"elora"}

    # Ensure PostgreSQL is running
    check_postgresql

    # Check if user exists
    if ! su - postgres -c "psql -tAc \"SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'\"" | grep -q 1; then
        log "Creating database user ${DB_USER}..."
        su - postgres -c "psql -c \"CREATE USER ${DB_USER} WITH LOGIN PASSWORD '${DB_PASSWORD}';\""
    else
        log "User ${DB_USER} already exists, updating password..."
        su - postgres -c "psql -c \"ALTER USER ${DB_USER} WITH PASSWORD '${DB_PASSWORD}';\""
    fi

    # Check if database exists
    if ! su - postgres -c "psql -lqt" | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
        log "Creating database ${DB_NAME}..."
        su - postgres -c "psql -c \"CREATE DATABASE ${DB_NAME} OWNER ${DB_USER};\""
    else
        log "Database ${DB_NAME} already exists, updating owner..."
        su - postgres -c "psql -c \"ALTER DATABASE ${DB_NAME} OWNER TO ${DB_USER};\""
    fi

    # Grant privileges
    log "Setting up database privileges..."
    su - postgres -c "psql -c \"GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO ${DB_USER};\""

    log "Database setup completed successfully"
}

# Run database migrations
run_migrations() {
    log "Running database migrations..."
    cd "${INSTALL_DIR}"

    # Ensure we're in the virtual environment
    source "${INSTALL_DIR}/venv/bin/activate" || error "Failed to activate virtual environment"

    # Check if alembic.ini exists
    if [ ! -f "alembic.ini" ]; then
        error "alembic.ini not found in installation directory"
    fi

    # Run migrations using venv python
    # export DATABASE_URL="postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}/${DB_NAME}"

    log "Running Alembic migrations..."
    "${INSTALL_DIR}/venv/bin/alembic" upgrade head || error "Failed to run database migrations"

    log "Database migrations completed successfully"
}


# Check Python version
check_python_version() {
    log "Checking Python version..."
    if ! command -v python3 &> /dev/null; then
        error "Python3 is not installed"
    fi


    local python_version=$(python3 -c 'import sys; print("%d.%d" % (sys.version_info.major, sys.version_info.minor))')
    log "Found Python version: $python_version"

    # Compare versions using numeric comparison
    local required_major=$(echo $PYTHON_MIN_VERSION | cut -d. -f1)
    local required_minor=$(echo $PYTHON_MIN_VERSION | cut -d. -f2)
    local found_major=$(echo $python_version | cut -d. -f1)
    local found_minor=$(echo $python_version | cut -d. -f2)

    if [ "$found_major" -lt "$required_major" ] ||
       ([ "$found_major" -eq "$required_major" ] && [ "$found_minor" -lt "$required_minor" ]); then
        error "Python version $PYTHON_MIN_VERSION or higher is required. Found version $python_version"
    fi

    log "Python version check passed"
}

# Backup function
backup_existing() {
    if [ -d "$INSTALL_DIR" ]; then
        local backup_dir="${INSTALL_DIR}_backup_$(date +%Y%m%d_%H%M%S)"
        log "Creating backup of existing installation to $backup_dir"
        mv "$INSTALL_DIR" "$backup_dir" || error "Failed to create backup"
    fi
}

# Create and configure installation directory
setup_install_dir() {
    log "Creating installation directory..."
    mkdir -p "$INSTALL_DIR" || error "Failed to create installation directory"

    # Set proper permissions
    chown -R root:root "$INSTALL_DIR"
    chmod -R 755 "$INSTALL_DIR"
}


# Function to install Python requirements with error handling
install_python_requirements() {
    log "Installing Python requirements in virtual environment..."

    # Change to installation directory
    cd "${INSTALL_DIR}" || error "Failed to change to installation directory"

    # Check if requirements.txt exists
    if [ ! -f "requirements.txt" ]; then
        error "requirements.txt not found in ${INSTALL_DIR}"
    fi

    # Ensure we're in the virtual environment
    source "${INSTALL_DIR}/venv/bin/activate" || error "Failed to activate virtual environment"

    "${INSTALL_DIR}/venv/bin/pip" install -r requirements.txt || error "Failed to install Python requirements"

    # Ensure alembic is installed in venv
    log "Verifying Alembic installation in virtual environment..."
    if ! "${INSTALL_DIR}/venv/bin/pip" show alembic > /dev/null; then
        log "Installing Alembic in virtual environment..."
        "${INSTALL_DIR}/venv/bin/pip" install alembic || error "Failed to install Alembic"
    fi

    log "Python requirements installed successfully"
}

# Create systemd service
create_service() {
    log "Creating systemd service..."
    cat > "/etc/systemd/system/${SERVICE_NAME}.service" << EOL
[Unit]
Description=Elora VPN Manager
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=${INSTALL_DIR}
Environment="PATH=${INSTALL_DIR}/venv/bin"
ExecStart=${INSTALL_DIR}/venv/bin/python main.py
Restart=always
RestartSec=3
StandardOutput=append:/var/log/${SERVICE_NAME}/${SERVICE_NAME}.log
StandardError=append:/var/log/${SERVICE_NAME}/${SERVICE_NAME}.log

[Install]
WantedBy=multi-user.target
EOL

    # Create log directory
    mkdir -p "/var/log/${SERVICE_NAME}"
    touch "/var/log/${SERVICE_NAME}/${SERVICE_NAME}.log"
    chmod 644 "/var/log/${SERVICE_NAME}/${SERVICE_NAME}.log"

    # Reload systemd
    systemctl daemon-reload || error "Failed to reload systemd"
}

# Update configuration
update_config() {
    log "Updating configuration..."
    local config_file="$INSTALL_DIR/static/config.json"

    # Create or update config.json
    cat > "$config_file" << EOL
{
    "GENERATE_SOURCEMAP": false,
    "BASE_NAME": "Elora",
    "BASE_DESCRIPTION": "Elora Panel",
    "BASE_PREFIX": "elora",
    "BASE_URL": "${PROTOCOL}://${DOMAIN}:${PORT}/api/",
    "NAME_MANIFEST": "manifest.json",
    "EXPIRE_AT": 30,
    "PATH_TO_LOGIN": "/accounts"
}
EOL
}

# Main installation process
main() {
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --domain)
                DOMAIN="$2"
                shift 2
                ;;
            --port)
                PORT="$2"
                shift 2
                ;;
            --protocol)
                PROTOCOL="$2"
                shift 2
                ;;
            --db-name)
                DB_NAME="$2"
                shift 2
                ;;
            --db-user)
                DB_USER="$2"
                shift 2
                ;;
            --db-pass)
                DB_PASSWORD="$2"
                shift 2
                ;;
            --jwt-secret)
                JWT_SECRET="$2"
                shift 2
                ;;
            *)
                error "Unknown option: $1"
                ;;
        esac
    done


    # Check if running as root
    if [ "$EUID" -ne 0 ]; then
        error "Please run as root or with sudo"
    fi

    # Check OS
    if [ ! -f /etc/os-release ]; then
        error "Cannot detect operating system"
    fi

    source /etc/os-release
    if [[ "$ID" != "ubuntu" && "$ID" != "debian" ]]; then
        error "This script is only for Ubuntu and Debian systems"
    fi

    log "Starting Elora VPN Manager installation..."

    # Check system and dependencies
    check_dependencies
    check_python_version

    # Backup existing installation
    backup_existing

    # Setup installation directory
    setup_install_dir

    # Setup database
    setup_database

    # Download and extract latest release
    check_download_tools
    download_latest_release

    # Setup virtual environment first
    setup_virtualenv

    # Then install requirements in the venv
    install_python_requirements

    # Update configurations
    update_env

    # Run database migrations
    run_migrations

    # Update configuration
    update_config

    # Create and start service
    create_service
    log "Enabling and starting service..."
    systemctl enable "$SERVICE_NAME" || error "Failed to enable service"
    systemctl start "$SERVICE_NAME" || warning "Failed to start service"

    # Final status check
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        # Print installation summary
        log "\nInstallation completed successfully!"

        log "\nInstallation Details:"
        log "- Panel URL: ${PROTOCOL}://${DOMAIN}:${PORT}"
        log "- Admin User Name: ${USER_NAME}"
        log "- Admin Password: ${PASSWORD}"

        log "\nConfigurations:"
        log "- Database: ${DB_NAME}"
        log "- Database User: ${DB_USER}"
        log "- Database Password: ${DB_PASSWORD}"
        log "- Installation Directory: ${INSTALL_DIR}"
        log "- Python Configuration File: ${INSTALL_DIR}/.env"
        log "- Front-end Configuration File: ${INSTALL_DIR}/static/config.json"
        log "- Service Name: ${SERVICE_NAME}"

        log "\nService Management Commands:"
        log "- Check status: systemctl status ${SERVICE_NAME}"
        log "- View logs: journalctl -u ${SERVICE_NAME} -f"
        log "- Restart service: systemctl restart ${SERVICE_NAME}"
    else
        warning "Service installation completed but service is not running"
        warning "Please check the logs: journalctl -u $SERVICE_NAME -n 50"
    fi
}

# Run main installation
main "$@"