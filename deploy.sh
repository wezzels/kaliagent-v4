#!/bin/bash
# Agentic AI Production Deployment Script
# Usage: ./deploy.sh [dev|staging|prod]

set -e

# Configuration
ENVIRONMENT=${1:-prod}
PROJECT_NAME="agentic-ai"
COMPOSE_FILE="docker-compose.prod.yaml"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi
    
    # Check if running as root (not recommended)
    if [ "$EUID" -eq 0 ]; then
        log_warning "Running as root is not recommended"
    fi
    
    log_success "Prerequisites check passed"
}

generate_secrets() {
    log_info "Generating secrets..."
    
    # Create .env file if it doesn't exist
    if [ ! -f .env ]; then
        cat > .env << EOF
# Agentic AI Environment Configuration
# Generated: $(date)

# PostgreSQL
POSTGRES_PASSWORD=$(openssl rand -base64 32)

# Application
SECRET_KEY=$(openssl rand -base64 32)

# Grafana
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=$(openssl rand -base64 16)

# Redis (optional password)
# REDIS_PASSWORD=
EOF
        chmod 600 .env
        log_success "Created .env file with secure secrets"
    else
        log_warning ".env file already exists, skipping generation"
    fi
}

create_directories() {
    log_info "Creating directories..."
    
    mkdir -p logs
    mkdir -p monitoring/grafana/dashboards
    mkdir -p monitoring/grafana/datasources
    mkdir -p scripts
    
    log_success "Directories created"
}

initialize_database() {
    log_info "Creating database initialization script..."
    
    cat > scripts/init-db.sql << 'EOF'
-- Agentic AI Database Initialization
-- This script runs on first startup

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create schema if not exists
CREATE SCHEMA IF NOT EXISTS agentic_ai;

-- Grant permissions
GRANT ALL PRIVILEGES ON SCHEMA agentic_ai TO postgres;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA agentic_ai TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA agentic_ai TO postgres;

EOF
    
    log_success "Database initialization script created"
}

deploy() {
    log_info "Deploying Agentic AI (${ENVIRONMENT})..."
    
    # Pull latest images
    log_info "Pulling latest images..."
    docker-compose -f ${COMPOSE_FILE} pull
    
    # Start services
    log_info "Starting services..."
    docker-compose -f ${COMPOSE_FILE} up -d
    
    # Wait for services to be healthy
    log_info "Waiting for services to be healthy..."
    sleep 30
    
    # Check service status
    docker-compose -f ${COMPOSE_FILE} ps
    
    log_success "Deployment complete!"
}

show_status() {
    log_info "Service Status:"
    echo ""
    docker-compose -f ${COMPOSE_FILE} ps
    echo ""
    
    log_info "Access URLs:"
    echo "  - API:         http://localhost:8000"
    echo "  - Dashboard:   http://localhost:3000"
    echo "  - Grafana:     http://localhost:3001 (admin/admin)"
    echo "  - Prometheus:  http://localhost:9090"
    echo "  - Redis UI:    http://localhost:8081"
    echo ""
}

show_logs() {
    log_info "Showing logs (Ctrl+C to stop)..."
    docker-compose -f ${COMPOSE_FILE} logs -f
}

backup() {
    log_info "Creating backup..."
    
    BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p ${BACKUP_DIR}
    
    # Backup PostgreSQL
    docker-compose -f ${COMPOSE_FILE} exec -T postgres pg_dump -U postgres agentic_ai > ${BACKUP_DIR}/database.sql
    
    # Backup volumes
    docker run --rm -v agentic-ai_redis_data:/data -v ${BACKUP_DIR}/redis:/backup alpine tar czf /backup/redis_data.tar.gz -C /data .
    docker run --rm -v agentic-ai_grafana_data:/data -v ${BACKUP_DIR}/grafana:/backup alpine tar czf /backup/grafana_data.tar.gz -C /data .
    
    log_success "Backup created in ${BACKUP_DIR}"
}

restore() {
    BACKUP_PATH=${1:-}
    
    if [ -z "${BACKUP_PATH}" ]; then
        log_error "Backup path required"
        echo "Usage: $0 restore <backup_path>"
        exit 1
    fi
    
    log_info "Restoring from ${BACKUP_PATH}..."
    
    # Restore PostgreSQL
    cat ${BACKUP_PATH}/database.sql | docker-compose -f ${COMPOSE_FILE} exec -T postgres psql -U postgres -d agentic_ai
    
    log_success "Restore complete"
}

cleanup() {
    log_warning "This will remove all containers, volumes, and networks!"
    read -p "Are you sure? (y/N) " confirm
    
    if [ "$confirm" = "y" ]; then
        log_info "Cleaning up..."
        docker-compose -f ${COMPOSE_FILE} down -v
        log_success "Cleanup complete"
    else
        log_info "Cleanup cancelled"
    fi
}

# Main
case "${2:-}" in
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    backup)
        backup
        ;;
    restore)
        restore "${3:-}"
        ;;
    cleanup)
        cleanup
        ;;
    *)
        check_prerequisites
        generate_secrets
        create_directories
        initialize_database
        deploy
        show_status
        ;;
esac
