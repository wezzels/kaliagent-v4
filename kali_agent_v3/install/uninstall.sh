#!/bin/bash
#===============================================================================
# KaliAgent v3 - Uninstallation Script
#===============================================================================
# 
# This script removes KaliAgent v3 from the system.
# 
# Usage: sudo ./uninstall.sh [--keep-data|--purge]
#
# Options:
#   --keep-data   Remove software but keep data and configs
#   --purge       Remove everything including data (default)
#
#===============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
INSTALL_DIR="/opt/kaliagent_v3"
CONFIG_DIR="/etc/kaliagent_v3"
DATA_DIR="/var/lib/kaliagent_v3"
LOG_DIR="/var/log/kaliagent_v3"
USER="kaliagent"
PURGE=true

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

parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --keep-data)
                PURGE=false
                shift
                ;;
            --purge)
                PURGE=true
                shift
                ;;
            *)
                log_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done
}

confirm_removal() {
    echo
    echo "==============================================================================="
    echo "  KaliAgent v3 Uninstallation"
    echo "==============================================================================="
    echo
    
    if [[ "$PURGE" == true ]]; then
        log_warning "This will remove EVERYTHING including:"
        echo "  - Installation: $INSTALL_DIR"
        echo "  - Configuration: $CONFIG_DIR"
        echo "  - Data: $DATA_DIR"
        echo "  - Logs: $LOG_DIR"
        echo "  - User account: $USER"
    else
        log_warning "This will remove software but keep data:"
        echo "  - Removing: $INSTALL_DIR"
        echo "  - Removing: $CONFIG_DIR"
        echo "  - Keeping: $DATA_DIR"
        echo "  - Keeping: $LOG_DIR"
    fi
    echo
    
    read -p "Are you sure you want to continue? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Uninstallation cancelled"
        exit 0
    fi
}

stop_service() {
    log_info "Stopping KaliAgent service..."
    
    if systemctl is-active --quiet kaliagent; then
        systemctl stop kaliagent
        log_success "Service stopped"
    else
        log_info "Service not running"
    fi
    
    systemctl disable kaliagent 2>/dev/null || true
    rm -f /etc/systemd/system/kaliagent.service
    systemctl daemon-reload
    
    log_success "Service removed"
}

remove_directories() {
    log_info "Removing directories..."
    
    # Always remove installation
    if [[ -d "$INSTALL_DIR" ]]; then
        rm -rf "$INSTALL_DIR"
        log_success "Removed: $INSTALL_DIR"
    fi
    
    # Always remove configuration
    if [[ -d "$CONFIG_DIR" ]]; then
        rm -rf "$CONFIG_DIR"
        log_success "Removed: $CONFIG_DIR"
    fi
    
    # Remove data and logs only if purging
    if [[ "$PURGE" == true ]]; then
        if [[ -d "$DATA_DIR" ]]; then
            rm -rf "$DATA_DIR"
            log_success "Removed: $DATA_DIR"
        fi
        
        if [[ -d "$LOG_DIR" ]]; then
            rm -rf "$LOG_DIR"
            log_success "Removed: $LOG_DIR"
        fi
    else
        log_info "Keeping data and logs"
    fi
}

remove_user() {
    log_info "Removing user account..."
    
    if id "$USER" &>/dev/null; then
        userdel -r "$USER" 2>/dev/null || userdel "$USER"
        log_success "User removed: $USER"
    else
        log_info "User does not exist"
    fi
}

remove_cli() {
    log_info "Removing CLI wrapper..."
    
    rm -f /usr/local/bin/kaliagent
    
    if [[ -f /usr/local/bin/kaliagent ]]; then
        log_error "Failed to remove CLI wrapper"
    else
        log_success "CLI wrapper removed"
    fi
}

cleanup() {
    log_info "Cleaning up..."
    
    # Remove from PATH if added
    # (Installation script doesn't modify PATH, so this is just precautionary)
    
    log_success "Cleanup complete"
}

print_summary() {
    echo
    echo "==============================================================================="
    echo "  KaliAgent v3 Uninstallation Complete"
    echo "==============================================================================="
    echo
    
    if [[ "$PURGE" == true ]]; then
        log_success "All files and configurations removed"
        echo
        echo "  Note: Your data has been permanently deleted."
    else
        log_success "Software removed, data preserved"
        echo
        echo "  Data preserved at:"
        echo "    - $DATA_DIR"
        echo "    - $LOG_DIR"
        echo
        echo "  To reinstall later:"
        echo "    sudo ./install.sh"
        echo "  Data will be available in the new installation."
    fi
    
    echo
    echo "==============================================================================="
    echo
}

main() {
    check_root
    parse_args "$@"
    confirm_removal
    
    echo
    log_info "Starting uninstallation..."
    echo
    
    stop_service
    remove_directories
    remove_user
    remove_cli
    cleanup
    print_summary
}

main "$@"
