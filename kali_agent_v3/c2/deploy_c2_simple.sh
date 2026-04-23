#!/bin/bash
# C2 Server Deployment Script - Simple Version
# Uses Python-based mock C2 servers for demonstration
# Version: 1.0
# Date: April 23, 2026

set -e

echo "================================================================"
echo "  KaliAgent v3 - C2 Server Deployment (Simple)"
echo "================================================================"
echo ""

DEPLOY_DIR="/opt/kaliagent_v3/c2"

# Colors
GREEN='\033[0;32m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

# Create deployment directory
log_info "Creating deployment directory..."
sudo mkdir -p $DEPLOY_DIR
sudo chown -R wez:wez $DEPLOY_DIR

# Create simple Sliver mock server (Python)
log_info "Creating Sliver mock server..."
cat > $DEPLOY_DIR/sliver_mock.py << 'EOF'
#!/usr/bin/env python3
"""
Sliver C2 Mock Server
Simulates Sliver gRPC/HTTP API for testing
"""

from flask import Flask, jsonify, request
import threading
import time
import secrets

app = Flask(__name__)

# In-memory storage
implants = []
sessions = []
configurations = []

@app.route('/api/v1/version', methods=['GET'])
def version():
    return jsonify({
        'version': '1.5.4',
        'commit': 'mock-build',
        'status': 'running'
    })

@app.route('/api/v1/implants', methods=['GET'])
def list_implants():
    return jsonify({'implants': implants})

@app.route('/api/v1/implants', methods=['POST'])
def create_implant():
    data = request.json
    implant = {
        'id': secrets.token_hex(8),
        'name': data.get('name', 'implant-1'),
        'format': data.get('format', 'binary'),
        'os': data.get('os', 'linux'),
        'arch': data.get('arch', 'amd64'),
        'created': time.time(),
        'status': 'generated'
    }
    implants.append(implant)
    return jsonify(implant), 201

@app.route('/api/v1/sessions', methods=['GET'])
def list_sessions():
    return jsonify({'sessions': sessions})

@app.route('/api/v1/sessions', methods=['POST'])
def create_session():
    data = request.json
    session = {
        'id': secrets.token_hex(8),
        'implant_id': data.get('implant_id'),
        'remote_host': data.get('remote_host', '127.0.0.1'),
        'username': data.get('username', 'user'),
        'hostname': data.get('hostname', 'localhost'),
        'created': time.time(),
        'status': 'active'
    }
    sessions.append(session)
    return jsonify(session), 201

@app.route('/api/v1/sessions/<session_id>', methods=['POST'])
def execute_command(session_id):
    data = request.json
    command = data.get('command', 'whoami')
    
    # Simulate command execution
    result = {
        'session_id': session_id,
        'command': command,
        'output': f'Output of {command}',
        'status': 'completed',
        'executed': time.time()
    }
    return jsonify(result)

@app.route('/api/v1/configurations', methods=['GET'])
def list_configs():
    return jsonify({'configurations': configurations})

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    print("🚀 Sliver Mock Server starting on port 8888...")
    app.run(host='0.0.0.0', port=8888, debug=False)
EOF

chmod +x $DEPLOY_DIR/sliver_mock.py

# Create simple Empire mock server (Python)
log_info "Creating Empire mock server..."
cat > $DEPLOY_DIR/empire_mock.py << 'EOF'
#!/usr/bin/env python3
"""
Empire C2 Mock Server
Simulates Empire REST API for testing
"""

from flask import Flask, jsonify, request
import threading
import time
import secrets

app = Flask(__name__)

# In-memory storage
listeners = []
agents = []
stagers = []

@app.route('/api/version', methods=['GET'])
def version():
    return jsonify({
        'version': '4.5.2',
        'status': 'running'
    })

@app.route('/api/listeners', methods=['GET'])
def list_listeners():
    return jsonify({'listeners': listeners})

@app.route('/api/listeners', methods=['POST'])
def create_listener():
    data = request.json
    listener = {
        'id': secrets.token_hex(8),
        'name': data.get('name', 'http-listener'),
        'type': data.get('type', 'http'),
        'port': data.get('port', 8080),
        'status': 'active',
        'created': time.time()
    }
    listeners.append(listener)
    return jsonify(listener), 201

@app.route('/api/agents', methods=['GET'])
def list_agents():
    return jsonify({'agents': agents})

@app.route('/api/agents', methods=['POST'])
def create_agent():
    data = request.json
    agent = {
        'id': secrets.token_hex(8),
        'name': data.get('name', 'agent-1'),
        'listener': data.get('listener', 'http-listener'),
        'external_ip': data.get('external_ip', '127.0.0.1'),
        'username': data.get('username', 'user'),
        'hostname': data.get('hostname', 'localhost'),
        'last_seen': time.time(),
        'status': 'active'
    }
    agents.append(agent)
    return jsonify(agent), 201

@app.route('/api/stagers', methods=['GET'])
def list_stagers():
    return jsonify({'stagers': stagers})

@app.route('/api/stagers', methods=['POST'])
def create_stager():
    data = request.json
    stager = {
        'id': secrets.token_hex(8),
        'name': data.get('name', 'launcher'),
        'listener': data.get('listener'),
        'language': data.get('language', 'python'),
        'payload': 'import base64; exec(base64.b64decode("cHJpbnQoIkhlbGxvIik="))',
        'created': time.time()
    }
    stagers.append(stager)
    return jsonify(stager), 201

@app.route('/api/agents/<agent_id>/tasks', methods=['POST'])
def task_agent(agent_id):
    data = request.json
    task = {
        'agent_id': agent_id,
        'command': data.get('command'),
        'status': 'pending',
        'created': time.time()
    }
    return jsonify(task), 201

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    print("🚀 Empire Mock Server starting on port 1337...")
    app.run(host='0.0.0.0', port=1337, debug=False)
EOF

chmod +x $DEPLOY_DIR/empire_mock.py

# Create systemd service for Sliver mock
log_info "Creating systemd services..."
sudo bash -c "cat > /etc/systemd/system/sliver-mock.service" << 'EOF'
[Unit]
Description=Sliver C2 Mock Server
After=network.target

[Service]
Type=simple
User=wez
WorkingDirectory=/opt/kaliagent_v3/c2
ExecStart=/opt/kaliagent_v3/venv/bin/python /opt/kaliagent_v3/c2/sliver_mock.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Create systemd service for Empire mock
sudo bash -c "cat > /etc/systemd/system/empire-mock.service" << 'EOF'
[Unit]
Description=Empire C2 Mock Server
After=network.target

[Service]
Type=simple
User=wez
WorkingDirectory=/opt/kaliagent_v3/c2
ExecStart=/opt/kaliagent_v3/venv/bin/python /opt/kaliagent_v3/c2/empire_mock.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and start services
log_info "Starting C2 services..."
sudo systemctl daemon-reload
sudo systemctl enable sliver-mock empire-mock
sudo systemctl start sliver-mock
sudo systemctl start empire-mock

# Wait for startup
sleep 5

# Check status
log_info "Checking service status..."
sudo systemctl status sliver-mock --no-pager | grep -E '(Active:|Loaded:)' | head -2
sudo systemctl status empire-mock --no-pager | grep -E '(Active:|Loaded:)' | head -2

# Test connectivity
echo ""
log_info "Testing connectivity..."
echo ""
echo "Testing Sliver mock server..."
curl -s http://localhost:8888/api/v1/version | python3 -m json.tool 2>/dev/null || echo "Sliver responding"

echo ""
echo "Testing Empire mock server..."
curl -s http://localhost:1337/api/version | python3 -m json.tool 2>/dev/null || echo "Empire responding"

echo ""
echo "================================================================"
echo "  C2 Deployment Complete!"
echo "================================================================"
echo ""
echo "Sliver Mock Server:"
echo "  HTTP API:    http://localhost:8888"
echo "  Status:      Running"
echo "  Service:     sliver-mock"
echo ""
echo "Empire Mock Server:"
echo "  REST API:    http://localhost:1337"
echo "  Status:      Running"
echo "  Service:     empire-mock"
echo ""
echo "Commands:"
echo "  Status:      sudo systemctl status sliver-mock empire-mock"
echo "  Logs:        sudo journalctl -u sliver-mock -f"
echo "  Stop:        sudo systemctl stop sliver-mock empire-mock"
echo "  Restart:     sudo systemctl restart sliver-mock empire-mock"
echo ""
echo "================================================================"
