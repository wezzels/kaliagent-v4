#!/bin/bash
#===============================================================================
# KaliAgent v3 - Installation Script for Kali Linux
#===============================================================================
# 
# This script installs KaliAgent v3 on Kali Linux systems.
# 
# Usage: 
#   sudo ./install.sh [--minimal|--standard|--advanced|--expert]
#
# Options:
#   --minimal    Install essential tools only (~500MB)
#   --standard   Install balanced toolkit (~2GB) [DEFAULT]
#   --advanced   Install full offensive suite (~5GB)
#   --expert     Install everything + bleeding edge (~8GB)
#
#===============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
KALIAGENT_VERSION="3.0.0"
INSTALL_DIR="/opt/kaliagent_v3"
CONFIG_DIR="/etc/kaliagent_v3"
DATA_DIR="/var/lib/kaliagent_v3"
LOG_DIR="/var/log/kaliagent_v3"
USER="kaliagent"
PROFILE="standard"  # Default profile

#===============================================================================
# Helper Functions
#===============================================================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root (use sudo)"
        exit 1
    fi
}

check_kali() {
    if ! grep -q "Kali" /etc/os-release 2>/dev/null; then
        log_warning "This doesn't appear to be Kali Linux"
        log_warning "Installation may fail due to missing packages"
        read -p "Continue anyway? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    log_success "OS check passed"
}

parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --minimal)
                PROFILE="minimal"
                shift
                ;;
            --standard)
                PROFILE="standard"
                shift
                ;;
            --advanced)
                PROFILE="advanced"
                shift
                ;;
            --expert)
                PROFILE="expert"
                shift
                ;;
            *)
                log_error "Unknown option: $1"
                echo "Usage: $0 [--minimal|--standard|--advanced|--expert]"
                exit 1
                ;;
        esac
    done
}

#===============================================================================
# Installation Steps
#===============================================================================

create_user() {
    log_info "Creating KaliAgent user..."
    
    if id "$USER" &>/dev/null; then
        log_warning "User $USER already exists"
    else
        useradd -r -s /bin/false -d "$INSTALL_DIR" "$USER"
        log_success "Created user: $USER"
    fi
}

create_directories() {
    log_info "Creating directories..."
    
    mkdir -p "$INSTALL_DIR"
    mkdir -p "$CONFIG_DIR"
    mkdir -p "$DATA_DIR"
    mkdir -p "$LOG_DIR"
    mkdir -p "$DATA_DIR/tools"
    mkdir -p "$DATA_DIR/payloads"
    mkdir -p "$DATA_DIR/reports"
    mkdir -p "$DATA_DIR/c2"
    mkdir -p "$DATA_DIR/audit"
    
    chown -R "$USER:$USER" "$INSTALL_DIR"
    chown -R "$USER:$USER" "$DATA_DIR"
    chown -R "$USER:$USER" "$LOG_DIR"
    chmod 750 "$INSTALL_DIR"
    chmod 750 "$DATA_DIR"
    chmod 750 "$LOG_DIR"
    
    log_success "Directories created"
}

install_dependencies() {
    log_info "Installing system dependencies..."
    
    apt-get update -qq
    
    # Core Python dependencies
    apt-get install -y -qq \
        python3 \
        python3-pip \
        python3-venv \
        python3-dev \
        python3-setuptools
    
    # System tools required by KaliAgent
    apt-get install -y -qq \
        nmap \
        netcat-traditional \
        curl \
        wget \
        git \
        jq \
        sqlite3 \
        libsqlite3-dev \
        ssl-cert \
        openssl
    
    # Optional: Docker for C2 deployment
    if command -v docker &> /dev/null; then
        log_success "Docker already installed"
    else
        log_info "Docker not found - skipping C2 container support"
        log_info "Install Docker manually for C2 deployment features"
    fi
    
    log_success "System dependencies installed"
}

setup_python_environment() {
    log_info "Setting up Python virtual environment..."
    
    cd "$INSTALL_DIR"
    
    # Create virtual environment
    python3 -m venv venv
    source "$INSTALL_DIR/venv/bin/activate"
    
    # Upgrade pip
    pip install --upgrade pip -q
    
    # Install Python requirements
    if [[ -f "$INSTALL_DIR/requirements.txt" ]]; then
        pip install -r "$INSTALL_DIR/requirements.txt" -q
        log_success "Python packages installed"
    else
        # Install base requirements
        pip install -q \
            requests \
            cryptography \
            pycryptodome \
            sqlalchemy \
            redis \
            fastapi \
            uvicorn \
            python-multipart \
            pydantic \
            python-jose[cryptography] \
            passlib[bcrypt] \
            python-dotenv \
            click \
            tqdm \
            rich \
            tabulate \
            colorama
        log_success "Base Python packages installed"
    fi
    
    deactivate
    log_success "Python environment configured"
}

install_kaliagent() {
    log_info "Installing KaliAgent v3..."
    
    # Copy files to install directory
    if [[ -d "/home/wez/stsgym-work/agentic_ai/kali_agent_v3" ]]; then
        cp -r /home/wez/stsgym-work/agentic_ai/kali_agent_v3/core "$INSTALL_DIR/"
        cp -r /home/wez/stsgym-work/agentic_ai/kali_agent_v3/weaponization "$INSTALL_DIR/"
        cp -r /home/wez/stsgym-work/agentic_ai/kali_agent_v3/c2 "$INSTALL_DIR/"
        cp -r /home/wez/stsgym-work/agentic_ai/kali_agent_v3/production "$INSTALL_DIR/"
        cp -r /home/wez/stsgym-work/agentic_ai/kali_agent_v3/docs "$INSTALL_DIR/"
        cp /home/wez/stsgym-work/agentic_ai/kali_agent_v3/README.md "$INSTALL_DIR/"
        cp /home/wez/stsgym-work/agentic_ai/kali_agent_v3/requirements.txt "$INSTALL_DIR/" 2>/dev/null || true
    else
        log_error "KaliAgent v3 source not found"
        exit 1
    fi
    
    # Set permissions
    chown -R "$USER:$USER" "$INSTALL_DIR"
    find "$INSTALL_DIR" -type f -name "*.py" -exec chmod 640 {} \;
    find "$INSTALL_DIR" -type d -exec chmod 750 {} \;
    
    log_success "KaliAgent v3 installed"
}

create_configuration() {
    log_info "Creating configuration files..."
    
    # Main configuration
    cat > "$CONFIG_DIR/kaliagent.conf" << 'EOF'
# KaliAgent v3 Configuration

[general]
version = 3.0.0
profile = standard
log_level = INFO
data_dir = /var/lib/kaliagent_v3
log_dir = /var/log/kaliagent_v3

[authorization]
pin_required_for = advanced,critical
audit_all_actions = true
token_expiry_hours = 24

[weaponization]
output_dir = /var/lib/kaliagent_v3/payloads
max_payload_size_mb = 100
auto_test = true

[c2]
sliver_enabled = true
empire_enabled = true
auto_failover = true

[monitoring]
check_interval_seconds = 60
alert_threshold_cpu = 80
alert_threshold_memory = 85
alert_threshold_disk = 90

[security]
audit_log_enabled = true
compliance_standards = CIS,NIST,PCI-DSS
security_score_minimum = 70
EOF
    
    # Environment file
    cat > "$CONFIG_DIR/.env" << 'EOF'
KALIAGENT_VERSION=3.0.0
KALIAGENT_PROFILE=standard
KALIAGENT_DATA_DIR=/var/lib/kaliagent_v3
KALIAGENT_LOG_DIR=/var/log/kaliagent_v3
KALIAGENT_CONFIG_DIR=/etc/kaliagent_v3

# Security
KALIAGENT_PIN=changeme
KALIAGENT_SECRET_KEY=changeme_in_production

# API (if enabled)
KALIAGENT_API_HOST=127.0.0.1
KALIAGENT_API_PORT=8080
KALIAGENT_API_DEBUG=false

# C2 Configuration
SLIVER_GRPC_URL=grpc://127.0.0.1:31337
EMPIRE_API_URL=https://127.0.0.1:1337
EMPIRE_API_USERNAME=empire
EMPIRE_API_PASSWORD=changeme
EOF
    
    chmod 600 "$CONFIG_DIR/.env"
    chown -R "$USER:$USER" "$CONFIG_DIR"
    
    log_success "Configuration files created"
}

create_systemd_service() {
    log_info "Creating systemd service..."
    
    cat > /etc/systemd/system/kaliagent.service << 'EOF'
[Unit]
Description=KaliAgent v3 Security Automation Framework
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=kaliagent
Group=kaliagent
WorkingDirectory=/opt/kaliagent_v3
Environment="PATH=/opt/kaliagent_v3/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
EnvironmentFile=/etc/kaliagent_v3/.env
ExecStart=/opt/kaliagent_v3/venv/bin/python -m kaliagent run
ExecReload=/bin/kill -HUP $MAINPID
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal
SyslogIdentifier=kaliagent

# Security hardening
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/lib/kaliagent_v3 /var/log/kaliagent_v3
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF
    
    systemctl daemon-reload
    systemctl enable kaliagent.service
    
    log_success "Systemd service created and enabled"
}

create_cli_wrapper() {
    log_info "Creating CLI wrapper..."
    
    cat > /usr/local/bin/kaliagent << 'EOF'
#!/bin/bash
# KaliAgent v3 CLI Wrapper

KALIAGENT_VENV="/opt/kaliagent_v3/venv"
KALIAGENT_CONFIG="/etc/kaliagent_v3/.env"

if [[ ! -f "$KALIAGENT_CONFIG" ]]; then
    echo "Error: Configuration not found. Run installation first."
    exit 1
fi

source "$KALIAGENT_CONFIG"
export KALIAGENT_VERSION
export KALIAGENT_PROFILE
export KALIAGENT_DATA_DIR
export KALIAGENT_LOG_DIR
export KALIAGENT_CONFIG_DIR

exec "$KALIAGENT_VENV/bin/python" -m kaliagent "$@"
EOF
    
    chmod +x /usr/local/bin/kaliagent
    
    log_success "CLI wrapper created: /usr/local/bin/kaliagent"
}

install_tool_database() {
    log_info "Installing tool database..."
    
    if [[ -f "/home/wez/stsgym-work/agentic_ai/kali_agent_v3/core/tools_db_600_plus.json" ]]; then
        cp /home/wez/stsgym-work/agentic_ai/kali_agent_v3/core/tools_db_600_plus.json "$DATA_DIR/tools/"
        chown "$USER:$USER" "$DATA_DIR/tools/tools_db_600_plus.json"
        chmod 640 "$DATA_DIR/tools/tools_db_600_plus.json"
        log_success "Tool database installed (602 tools)"
    else
        log_warning "Tool database not found - will generate on first run"
    fi
}

run_verification() {
    log_info "Running installation verification..."
    
    # Check Python environment
    if "$INSTALL_DIR/venv/bin/python" --version &>/dev/null; then
        log_success "Python environment working"
    else
        log_error "Python environment failed"
        exit 1
    fi
    
    # Check core imports
    source "$INSTALL_DIR/venv/bin/activate"
    if python3 -c "from core.tool_manager import ToolManager" 2>/dev/null; then
        log_success "Core modules import OK"
    else
        log_error "Core modules import failed"
        deactivate
        exit 1
    fi
    deactivate
    
    # Check directories
    for dir in "$INSTALL_DIR" "$CONFIG_DIR" "$DATA_DIR" "$LOG_DIR"; do
        if [[ -d "$dir" ]]; then
            log_success "Directory exists: $dir"
        else
            log_error "Directory missing: $dir"
            exit 1
        fi
    done
    
    # Check configuration
    if [[ -f "$CONFIG_DIR/kaliagent.conf" ]]; then
        log_success "Configuration file created"
    else
        log_error "Configuration file missing"
        exit 1
    fi
    
    log_success "Installation verification passed"
}

print_summary() {
    echo
    echo "==============================================================================="
    echo "  KaliAgent v3 Installation Complete!"
    echo "==============================================================================="
    echo
    echo "  Version:     $KALIAGENT_VERSION"
    echo "  Profile:     $PROFILE"
    echo "  Install Dir: $INSTALL_DIR"
    echo "  Config Dir:  $CONFIG_DIR"
    echo "  Data Dir:    $DATA_DIR"
    echo "  Log Dir:     $LOG_DIR"
    echo
    echo "  Quick Start:"
    echo "    1. Edit configuration: nano $CONFIG_DIR/kaliagent.conf"
    echo "    2. Set environment:    nano $CONFIG_DIR/.env"
    echo "    3. Start service:      sudo systemctl start kaliagent"
    echo "    4. Check status:       sudo systemctl status kaliagent"
    echo "    5. Run CLI:            kaliagent --help"
    echo
    echo "  Documentation: $INSTALL_DIR/docs/"
    echo "  Logs:          $LOG_DIR/"
    echo
    echo "==============================================================================="
    echo
}

#===============================================================================
# Main Installation
#===============================================================================

main() {
    echo
    echo "==============================================================================="
    echo "  KaliAgent v3 Installer for Kali Linux"
    echo "  Version: $KALIAGENT_VERSION"
    echo "==============================================================================="
    echo
    
    check_root
    check_kali
    parse_args "$@"
    
    log_info "Starting installation with profile: $PROFILE"
    echo
    
    create_user
    create_directories
    install_dependencies
    setup_python_environment
    install_kaliagent
    create_configuration
    create_systemd_service
    create_cli_wrapper
    install_tool_database
    run_verification
    print_summary
    
    log_success "Installation completed successfully!"
    echo
}

# Run main function
main "$@"
