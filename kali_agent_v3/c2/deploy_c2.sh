#!/bin/bash
# C2 Server Deployment Script
# Deploys Sliver and Empire C2 servers on Docker
# Version: 1.0
# Date: April 23, 2026

set -e

echo "================================================================"
echo "  KaliAgent v3 - C2 Server Deployment"
echo "================================================================"
echo ""

# Configuration
DEPLOY_DIR="/opt/kaliagent_v3/c2"
SLIVER_PORT=50051
EMPIRE_PORT=1337

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prereqs() {
    log_info "Checking prerequisites..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker not found. Installing..."
        sudo apt-get update -qq
        sudo apt-get install -y -qq docker.io docker-compose
        sudo systemctl start docker
        sudo systemctl enable docker
    fi
    
    if ! sudo docker ps &> /dev/null; then
        log_error "Cannot connect to Docker daemon"
        exit 1
    fi
    
    log_info "✓ Docker is running"
}

# Create deployment directory
setup_dirs() {
    log_info "Creating deployment directories..."
    
    sudo mkdir -p $DEPLOY_DIR
    sudo mkdir -p $DEPLOY_DIR/certs
    sudo mkdir -p $DEPLOY_DIR/sliver-config
    sudo mkdir -p $DEPLOY_DIR/empire-config
    sudo mkdir -p $DEPLOY_DIR/stagers
    
    sudo chown -R $USER:$USER $DEPLOY_DIR
    
    log_info "✓ Directories created"
}

# Generate TLS certificates
generate_certs() {
    log_info "Generating TLS certificates..."
    
    cd $DEPLOY_DIR/certs
    
    # Generate self-signed certificate
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout sliver.key \
        -out sliver.crt \
        -subj "/C=US/ST=State/L=City/O=Organization/CN=sliver-c2" \
        2>/dev/null
    
    # Set permissions
    chmod 600 sliver.key
    chmod 644 sliver.crt
    
    log_info "✓ Certificates generated"
}

# Create Sliver configuration
create_sliver_config() {
    log_info "Creating Sliver configuration..."
    
    cat > $DEPLOY_DIR/sliver-config/config.json << EOF
{
    "server": {
        "bind": "0.0.0.0",
        "port": 50051,
        "grpc_certs": {
            "cert": "/etc/sliver/certs/sliver.crt",
            "key": "/etc/sliver/certs/sliver.key"
        }
    },
    "c2": {
        "http": {
            "enabled": true,
            "port": 8888
        },
        "https": {
            "enabled": true,
            "port": 443,
            "cert": "/etc/sliver/certs/sliver.crt",
            "key": "/etc/sliver/certs/sliver.key"
        },
        "dns": {
            "enabled": true,
            "port": 53
        }
    }
}
EOF
    
    log_info "✓ Sliver configuration created"
}

# Create Empire configuration
create_empire_config() {
    log_info "Creating Empire configuration..."
    
    cat > $DEPLOY_DIR/empire-config/empire.yaml << EOF
# Empire C2 Configuration
rest_api:
    host: "0.0.0.0"
    port: 1337
    username: "empireadmin"
    password: "SecurePassword123!"

listeners:
    http:
        enabled: true
        port: 8080
        name: "http-listener"
    
    https:
        enabled: true
        port: 4443
        name: "https-listener"
        cert_path: "/empire/certs/empire.crt"
        key_path: "/empire/certs/empire.key"

database:
    url: "sqlite:////empire/server/data.db"
EOF
    
    log_info "✓ Empire configuration created"
}

# Deploy Sliver
deploy_sliver() {
    log_info "Deploying Sliver C2 server..."
    
    cd $DEPLOY_DIR
    
    # Copy Docker Compose file
    cp /home/wez/stsgym-work/agentic_ai/kali_agent_v3/c2/docker-compose.sliver.yml .
    
    # Start Sliver
    sudo docker-compose -f docker-compose.sliver.yml up -d
    
    # Wait for startup
    log_info "Waiting for Sliver to start (30 seconds)..."
    sleep 30
    
    # Check status
    if sudo docker ps | grep -q sliver-c2; then
        log_info "✓ Sliver C2 is running"
        sudo docker logs sliver-c2 --tail 20
    else
        log_error "Sliver C2 failed to start"
        return 1
    fi
}

# Deploy Empire
deploy_empire() {
    log_info "Deploying Empire C2 server..."
    
    cd $DEPLOY_DIR
    
    # Copy Docker Compose file
    cp /home/wez/stsgym-work/agentic_ai/kali_agent_v3/c2/docker-compose.empire.yml .
    
    # Start Empire
    sudo docker-compose -f docker-compose.empire.yml up -d
    
    # Wait for startup
    log_info "Waiting for Empire to start (60 seconds)..."
    sleep 60
    
    # Check status
    if sudo docker ps | grep -q empire-c2; then
        log_info "✓ Empire C2 is running"
        sudo docker logs empire-c2 --tail 20
    else
        log_error "Empire C2 failed to start"
        return 1
    fi
}

# Test connectivity
test_connectivity() {
    log_info "Testing C2 connectivity..."
    
    echo ""
    echo "Testing Sliver gRPC API..."
    if curl -s http://localhost:8888 > /dev/null 2>&1; then
        log_info "✓ Sliver HTTP C2 responding"
    else
        log_warn "Sliver HTTP C2 not responding (may need more time)"
    fi
    
    echo ""
    echo "Testing Empire REST API..."
    if curl -s http://localhost:1337/api/version > /dev/null 2>&1; then
        log_info "✓ Empire REST API responding"
    else
        log_warn "Empire REST API not responding (may need more time)"
    fi
}

# Print access information
print_info() {
    echo ""
    echo "================================================================"
    echo "  C2 Deployment Complete!"
    echo "================================================================"
    echo ""
    echo "Sliver C2:"
    echo "  gRPC API:    localhost:$SLIVER_PORT"
    echo "  HTTP C2:     localhost:8888"
    echo "  HTTPS C2:    localhost:443"
    echo "  DNS C2:      localhost:53"
    echo "  Container:   sliver-c2"
    echo ""
    echo "Empire C2:"
    echo "  REST API:    localhost:$EMPIRE_PORT"
    echo "  HTTP:        localhost:8080"
    echo "  HTTPS:       localhost:4443"
    echo "  Username:    empireadmin"
    echo "  Password:    SecurePassword123!"
    echo "  Container:   empire-c2"
    echo ""
    echo "Commands:"
    echo "  View logs:   sudo docker logs -f <container>"
    echo "  Stop:        sudo docker-compose -f docker-compose.<name>.yml down"
    echo "  Restart:     sudo docker-compose -f docker-compose.<name>.yml restart"
    echo ""
    echo "================================================================"
}

# Main deployment
main() {
    check_prereqs
    setup_dirs
    generate_certs
    create_sliver_config
    create_empire_config
    deploy_sliver
    deploy_empire
    test_connectivity
    print_info
    
    log_info "C2 deployment complete!"
}

# Run main
main "$@"
