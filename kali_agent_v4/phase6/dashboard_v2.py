#!/usr/bin/env python3
"""
KaliAgent v4 - Phase 6: Professional Dashboard v2
Modern web interface with real-time updates, dark theme, and data visualization
"""

from flask import Flask, render_template_string, jsonify, request, send_from_directory
from flask_socketio import SocketIO, emit
import json
import os
from datetime import datetime
from typing import Dict, List

app = Flask(__name__)
app.config['SECRET_KEY'] = 'kaliagent-v4-dashboard-secret'
socketio = SocketIO(app, cors_allowed_origins="*")

# In-memory state (would use Redis in production)
dashboard_state = {
    'lab_status': {
        'network': 'online',
        'juice_shop': 'running',
        'c2_servers': {
            'sliver': {'status': 'active', 'port': 8888},
            'empire': {'status': 'active', 'port': 1337},
            'enhanced': {'status': 'active', 'port': 8889}
        }
    },
    'active_attacks': [],
    'recent_findings': [],
    'attack_history': [],
    'system_stats': {
        'cpu_usage': 23.5,
        'memory_usage': 45.2,
        'disk_usage': 67.8,
        'network_rx': 1024.5,
        'network_tx': 512.3
    }
}

# HTML Template with modern dark theme
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KaliAgent v4 - Command Dashboard</title>
    <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {
            --bg-primary: #0a0a0f;
            --bg-secondary: #1a1a2e;
            --bg-card: #16213e;
            --accent-primary: #e94560;
            --accent-secondary: #0f3460;
            --text-primary: #ffffff;
            --text-secondary: #a0a0a0;
            --success: #00ff88;
            --warning: #ffaa00;
            --danger: #ff4444;
            --info: #00d4ff;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            min-height: 100vh;
        }
        
        .header {
            background: linear-gradient(135deg, var(--bg-secondary), var(--accent-secondary));
            padding: 20px 40px;
            border-bottom: 2px solid var(--accent-primary);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .header h1 {
            font-size: 24px;
            font-weight: 600;
            letter-spacing: 2px;
        }
        
        .header .status {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: var(--success);
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .container {
            max-width: 1600px;
            margin: 0 auto;
            padding: 30px;
        }
        
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .card {
            background: var(--bg-card);
            border-radius: 12px;
            padding: 20px;
            border: 1px solid var(--accent-secondary);
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }
        
        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid var(--accent-secondary);
        }
        
        .card-title {
            font-size: 16px;
            font-weight: 600;
            color: var(--accent-primary);
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .stat-value {
            font-size: 32px;
            font-weight: 700;
            color: var(--text-primary);
        }
        
        .stat-label {
            font-size: 12px;
            color: var(--text-secondary);
            text-transform: uppercase;
        }
        
        .progress-bar {
            width: 100%;
            height: 8px;
            background: var(--bg-secondary);
            border-radius: 4px;
            overflow: hidden;
            margin-top: 10px;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, var(--accent-primary), var(--info));
            transition: width 0.5s ease;
        }
        
        .attack-list {
            list-style: none;
        }
        
        .attack-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px;
            background: var(--bg-secondary);
            border-radius: 8px;
            margin-bottom: 10px;
            border-left: 3px solid var(--accent-primary);
        }
        
        .attack-item.success { border-left-color: var(--success); }
        .attack-item.running { border-left-color: var(--info); }
        .attack-item.failed { border-left-color: var(--danger); }
        
        .btn {
            background: var(--accent-primary);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .btn:hover {
            background: #ff5a7a;
            transform: translateY(-2px);
        }
        
        .btn-success { background: var(--success); }
        .btn-success:hover { background: #00ff99; }
        
        .btn-danger { background: var(--danger); }
        .btn-danger:hover { background: #ff6666; }
        
        .terminal {
            background: #0a0a0a;
            border: 1px solid var(--accent-secondary);
            border-radius: 8px;
            padding: 15px;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            height: 300px;
            overflow-y: auto;
        }
        
        .terminal-line {
            margin-bottom: 5px;
            color: var(--success);
        }
        
        .terminal-line.error { color: var(--danger); }
        .terminal-line.warning { color: var(--warning); }
        .terminal-line.info { color: var(--info); }
        
        .network-map {
            background: var(--bg-secondary);
            border-radius: 8px;
            padding: 20px;
            height: 400px;
            position: relative;
        }
        
        .node {
            position: absolute;
            width: 80px;
            height: 80px;
            background: var(--bg-card);
            border: 2px solid var(--accent-primary);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 11px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .node:hover {
            transform: scale(1.1);
            box-shadow: 0 0 20px var(--accent-primary);
        }
        
        .node.target { border-color: var(--danger); }
        .node.attacker { border-color: var(--success); }
        
        .badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
        }
        
        .badge-success { background: var(--success); color: #000; }
        .badge-warning { background: var(--warning); color: #000; }
        .badge-danger { background: var(--danger); color: #fff; }
        .badge-info { background: var(--info); color: #000; }
        
        .chart-container {
            position: relative;
            height: 250px;
        }
        
        .action-panel {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        
        .action-btn {
            background: var(--bg-secondary);
            border: 1px solid var(--accent-secondary);
            color: var(--text-primary);
            padding: 15px;
            border-radius: 8px;
            cursor: pointer;
            text-align: center;
            transition: all 0.3s ease;
        }
        
        .action-btn:hover {
            background: var(--accent-secondary);
            border-color: var(--accent-primary);
        }
        
        .action-btn i {
            font-size: 24px;
            margin-bottom: 8px;
            display: block;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🍀 KALIAGENT V4 <span style="color: var(--accent-primary);">COMMAND DASHBOARD</span></h1>
        <div class="status">
            <div class="status-indicator"></div>
            <span>SYSTEM OPERATIONAL</span>
            <span id="clock" style="margin-left: 20px; color: var(--text-secondary);"></span>
        </div>
    </div>
    
    <div class="container">
        <!-- System Stats Row -->
        <div class="grid">
            <div class="card">
                <div class="card-header">
                    <span class="card-title">CPU Usage</span>
                    <span class="badge badge-info">Real-time</span>
                </div>
                <div class="stat-value" id="cpu-stat">23.5%</div>
                <div class="progress-bar">
                    <div class="progress-fill" id="cpu-progress" style="width: 23.5%"></div>
                </div>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <span class="card-title">Memory Usage</span>
                    <span class="badge badge-info">Real-time</span>
                </div>
                <div class="stat-value" id="mem-stat">45.2%</div>
                <div class="progress-bar">
                    <div class="progress-fill" id="mem-progress" style="width: 45.2%"></div>
                </div>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <span class="card-title">Disk Usage</span>
                    <span class="badge badge-warning">Monitor</span>
                </div>
                <div class="stat-value" id="disk-stat">67.8%</div>
                <div class="progress-bar">
                    <div class="progress-fill" id="disk-progress" style="width: 67.8%"></div>
                </div>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <span class="card-title">Network Activity</span>
                    <span class="badge badge-success">Active</span>
                </div>
                <div class="stat-value" id="net-stat">1.5 MB/s</div>
                <div class="stat-label">RX: <span id="net-rx">1024.5</span> KB/s | TX: <span id="net-tx">512.3</span> KB/s</div>
            </div>
        </div>
        
        <!-- Lab Status & Active Attacks -->
        <div class="grid">
            <div class="card">
                <div class="card-header">
                    <span class="card-title">🔬 Lab Infrastructure</span>
                    <span class="badge badge-success">All Systems Online</span>
                </div>
                <div style="margin-top: 15px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                        <span>Isolated Network (10.0.100.0/24)</span>
                        <span class="badge badge-success">Online</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                        <span>OWASP Juice Shop</span>
                        <span class="badge badge-success">http://100.116.156.61:3000</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                        <span>Sliver C2</span>
                        <span class="badge badge-success">Port 8888</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                        <span>Empire C2</span>
                        <span class="badge badge-success">Port 1337</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span>Enhanced C2</span>
                        <span class="badge badge-success">Port 8889</span>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <span class="card-title">⚔️ Active Attacks</span>
                    <button class="btn" onclick="startNewAttack()">+ New Attack</button>
                </div>
                <ul class="attack-list" id="attack-list">
                    <li class="attack-item success">
                        <div>
                            <strong>SQL Injection - Juice Shop</strong>
                            <div style="font-size: 11px; color: var(--text-secondary);">Completed 2 minutes ago</div>
                        </div>
                        <span class="badge badge-success">Success</span>
                    </li>
                    <li class="attack-item running">
                        <div>
                            <strong>WiFi Deauth - Target Network</strong>
                            <div style="font-size: 11px; color: var(--text-secondary);">Running for 5 minutes</div>
                        </div>
                        <span class="badge badge-info">Running</span>
                    </li>
                </ul>
            </div>
        </div>
        
        <!-- Network Map & Terminal -->
        <div class="grid">
            <div class="card">
                <div class="card-header">
                    <span class="card-title">🌐 Network Topology</span>
                </div>
                <div class="network-map">
                    <div class="node attacker" style="top: 50%; left: 10%; transform: translate(0, -50%);">
                        🎯 Attack<br>Machine
                    </div>
                    <div class="node" style="top: 20%; left: 50%; transform: translate(-50%, -50%);">
                        🖥️ Juice<br>Shop
                    </div>
                    <div class="node target" style="top: 80%; left: 50%; transform: translate(-50%, -50%);">
                        💻 Windows<br>Target
                    </div>
                    <div class="node" style="top: 50%; left: 90%; transform: translate(-50%, -50%);">
                        🐧 Linux<br>Target
                    </div>
                </div>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <span class="card-title">💻 Live Terminal</span>
                    <button class="btn btn-success" onclick="clearTerminal()">Clear</button>
                </div>
                <div class="terminal" id="terminal">
                    <div class="terminal-line info">[2026-04-24 05:55:00] KaliAgent v4 Dashboard initialized</div>
                    <div class="terminal-line">[2026-04-24 05:55:01] Connecting to C2 servers...</div>
                    <div class="terminal-line success">[2026-04-24 05:55:02] Sliver C2 connected (port 8888)</div>
                    <div class="terminal-line success">[2026-04-24 05:55:02] Empire C2 connected (port 1337)</div>
                    <div class="terminal-line success">[2026-04-24 05:55:03] Enhanced C2 connected (port 8889)</div>
                    <div class="terminal-line info">[2026-04-24 05:55:04] Lab network verified (10.0.100.0/24)</div>
                    <div class="terminal-line">[2026-04-24 05:55:05] Waiting for commands...</div>
                </div>
            </div>
        </div>
        
        <!-- Quick Actions -->
        <div class="card">
            <div class="card-header">
                <span class="card-title">⚡ Quick Actions</span>
            </div>
            <div class="action-panel">
                <div class="action-btn" onclick="runAction('scan_network')">
                    <i>🔍</i>
                    <div>Scan Network</div>
                </div>
                <div class="action-btn" onclick="runAction('sql_injection')">
                    <i>💉</i>
                    <div>SQL Injection</div>
                </div>
                <div class="action-btn" onclick="runAction('wifi_deauth')">
                    <i>📡</i>
                    <div>WiFi Deauth</div>
                </div>
                <div class="action-btn" onclick="runAction('generate_payload')">
                    <i>🎯</i>
                    <div>Generate Payload</div>
                </div>
                <div class="action-btn" onclick="runAction('exploit_eternalblue')">
                    <i>💣</i>
                    <div>EternalBlue</div>
                </div>
                <div class="action-btn" onclick="runAction('generate_report')">
                    <i>📄</i>
                    <div>Generate Report</div>
                </div>
            </div>
        </div>
        
        <!-- Attack History Chart -->
        <div class="card" style="margin-top: 20px;">
            <div class="card-header">
                <span class="card-title">📊 Attack History (Last 24 Hours)</span>
            </div>
            <div class="chart-container">
                <canvas id="attackChart"></canvas>
            </div>
        </div>
    </div>
    
    <script>
        // Socket.IO connection
        const socket = io();
        
        // Update clock
        function updateClock() {
            const now = new Date();
            document.getElementById('clock').textContent = now.toISOString().replace('T', ' ').substr(0, 19) + ' UTC';
        }
        setInterval(updateClock, 1000);
        updateClock();
        
        // Receive real-time updates
        socket.on('update_stats', (data) => {
            document.getElementById('cpu-stat').textContent = data.cpu.toFixed(1) + '%';
            document.getElementById('cpu-progress').style.width = data.cpu + '%';
            document.getElementById('mem-stat').textContent = data.memory.toFixed(1) + '%';
            document.getElementById('mem-progress').style.width = data.memory + '%';
            document.getElementById('disk-stat').textContent = data.disk.toFixed(1) + '%';
            document.getElementById('disk-progress').style.width = data.disk + '%';
            document.getElementById('net-rx').textContent = data.net_rx.toFixed(1);
            document.getElementById('net-tx').textContent = data.net_tx.toFixed(1);
        });
        
        socket.on('terminal_output', (data) => {
            const terminal = document.getElementById('terminal');
            const line = document.createElement('div');
            line.className = 'terminal-line ' + (data.type || '');
            line.textContent = `[${data.timestamp}] ${data.message}`;
            terminal.appendChild(line);
            terminal.scrollTop = terminal.scrollHeight;
        });
        
        socket.on('attack_update', (data) => {
            // Update attack list
            console.log('Attack update:', data);
        });
        
        // Terminal logging
        function addTerminalLine(message, type = '') {
            socket.emit('log', { message, type });
        }
        
        // Clear terminal
        function clearTerminal() {
            document.getElementById('terminal').innerHTML = '';
            addTerminalLine('Terminal cleared', 'info');
        }
        
        // Start new attack
        function startNewAttack() {
            const target = prompt('Enter target IP/hostname:');
            if (target) {
                const attackType = prompt('Attack type (sql/wifi/network/exploit):');
                if (attackType) {
                    addTerminalLine(`Starting ${attackType} attack on ${target}`, 'info');
                    socket.emit('start_attack', { target, type: attackType });
                }
            }
        }
        
        // Run quick action
        function runAction(action) {
            addTerminalLine(`Executing: ${action}`, 'info');
            socket.emit('action', { action });
        }
        
        // Attack history chart
        const ctx = document.getElementById('attackChart').getContext('2d');
        const attackChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['00:00', '03:00', '06:00', '09:00', '12:00', '15:00', '18:00', '21:00'],
                datasets: [{
                    label: 'Successful Attacks',
                    data: [2, 5, 3, 8, 5, 12, 9, 15],
                    borderColor: '#00ff88',
                    backgroundColor: 'rgba(0, 255, 136, 0.1)',
                    tension: 0.4,
                    fill: true
                }, {
                    label: 'Failed Attacks',
                    data: [0, 1, 0, 2, 1, 3, 1, 2],
                    borderColor: '#ff4444',
                    backgroundColor: 'rgba(255, 68, 68, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: { color: '#ffffff' }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: '#1a1a2e' },
                        ticks: { color: '#a0a0a0' }
                    },
                    x: {
                        grid: { color: '#1a1a2e' },
                        ticks: { color: '#a0a0a0' }
                    }
                }
            }
        });
        
        // Request initial stats
        socket.emit('request_stats');
    </script>
</body>
</html>
"""

@app.route('/')
def dashboard():
    return render_template_string(DASHBOARD_HTML)

@socketio.on('connect')
def handle_connect():
    print('Client connected to dashboard')
    emit('update_stats', dashboard_state['system_stats'])

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('request_stats')
def handle_request_stats():
    emit('update_stats', dashboard_state['system_stats'])

@socketio.on('log')
def handle_log(data):
    message = data.get('message', '')
    msg_type = data.get('type', '')
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Broadcast to all clients
    emit('terminal_output', {
        'timestamp': timestamp,
        'message': message,
        'type': msg_type
    }, broadcast=True)

@socketio.on('start_attack')
def handle_start_attack(data):
    target = data.get('target', '')
    attack_type = data.get('type', '')
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Add to active attacks
    attack_id = f"attack_{datetime.now().timestamp()}"
    dashboard_state['active_attacks'].append({
        'id': attack_id,
        'target': target,
        'type': attack_type,
        'status': 'running',
        'started_at': timestamp
    })
    
    emit('terminal_output', {
        'timestamp': timestamp,
        'message': f'Started {attack_type} attack on {target}',
        'type': 'info'
    }, broadcast=True)
    
    emit('attack_update', {
        'action': 'started',
        'attack': dashboard_state['active_attacks'][-1]
    }, broadcast=True)

@socketio.on('action')
def handle_action(data):
    action = data.get('action', '')
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    emit('terminal_output', {
        'timestamp': timestamp,
        'message': f'Executing action: {action}',
        'type': 'info'
    }, broadcast=True)

if __name__ == '__main__':
    print("🍀 Starting KaliAgent v4 Dashboard v2...")
    print("📊 Access: http://localhost:5007")
    socketio.run(app, host='0.0.0.0', port=5007, debug=False)
