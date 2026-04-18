#!/usr/bin/env python3
"""
Agentic AI Dashboard v2.0 - Professional Backend Server
With WebSocket support for real-time graphs and live metrics
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import Dict, List, Optional
import asyncio
import json
import random
from datetime import datetime
import uvicorn

# =============================================================================
# Application Setup
# =============================================================================

app = FastAPI(
    title="Agentic AI Dashboard v2.0",
    description="Professional monitoring dashboard with live graphs and interactive agent drill-downs",
    version="2.0.0"
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================================================
# Data Models
# =============================================================================

class AgentStatus(BaseModel):
    name: str
    type: str
    status: str  # online, offline, busy
    capabilities: List[str]
    requests_per_minute: int
    avg_latency_ms: float
    success_rate: float
    last_active: str

class MetricPoint(BaseModel):
    timestamp: str
    value: float

class LiveMetrics(BaseModel):
    total_requests: int
    active_agents: int
    avg_latency: float
    error_rate: float
    requests_per_second: float

class CyberAgent(BaseModel):
    name: str
    icon: str
    description: str
    capabilities: List[str]
    tools_available: int
    active_engagements: int
    success_rate: float

# =============================================================================
# Mock Data (Replace with real database queries)
# =============================================================================

AGENTS = {
    "soc": AgentStatus(
        name="SOC Agent",
        type="security",
        status="online",
        capabilities=["24/7 Monitoring", "Incident Response", "Alert Triage", "SLA Tracking"],
        requests_per_minute=245,
        avg_latency_ms=45.2,
        success_rate=99.8,
        last_active=datetime.utcnow().isoformat()
    ),
    "vulnman": AgentStatus(
        name="VulnMan Agent",
        type="security",
        status="online",
        capabilities=["Vulnerability Scanning", "Risk Assessment", "Remediation Tracking", "Jira Integration"],
        requests_per_minute=189,
        avg_latency_ms=67.3,
        success_rate=99.5,
        last_active=datetime.utcnow().isoformat()
    ),
    "redteam": AgentStatus(
        name="RedTeam Agent",
        type="security",
        status="online",
        capabilities=["Penetration Testing", "Exploit Automation", "Kill Chain Simulation", "PDF Reporting"],
        requests_per_minute=156,
        avg_latency_ms=89.1,
        success_rate=98.9,
        last_active=datetime.utcnow().isoformat()
    ),
    "malware": AgentStatus(
        name="Malware Agent",
        type="security",
        status="online",
        capabilities=["Reverse Engineering", "Static Analysis", "Dynamic Analysis", "YARA Rules"],
        requests_per_minute=78,
        avg_latency_ms=234.5,
        success_rate=99.2,
        last_active=datetime.utcnow().isoformat()
    ),
    "security": AgentStatus(
        name="Security Agent",
        type="security",
        status="online",
        capabilities=["Threat Detection", "Pattern Matching", "IOC Search", "SIEM Integration"],
        requests_per_minute=312,
        avg_latency_ms=34.7,
        success_rate=99.9,
        last_active=datetime.utcnow().isoformat()
    ),
    "cloudsec": AgentStatus(
        name="CloudSecurity Agent",
        type="security",
        status="online",
        capabilities=["AWS CSPM", "Azure Security", "GCP Scanning", "Compliance Checking"],
        requests_per_minute=198,
        avg_latency_ms=56.8,
        success_rate=99.6,
        last_active=datetime.utcnow().isoformat()
    ),
}

CYBER_AGENTS = [
    CyberAgent(
        name="SOC Agent",
        icon="🛡️",
        description="24/7 security monitoring and incident response automation",
        capabilities=["Real-time monitoring", "Alert triage", "Incident management", "SLA tracking"],
        tools_available=12,
        active_engagements=3,
        success_rate=99.8
    ),
    CyberAgent(
        name="VulnMan Agent",
        icon="🔍",
        description="Complete vulnerability lifecycle management",
        capabilities=["Asset discovery", "Vulnerability scanning", "Risk scoring", "Auto-remediation"],
        tools_available=15,
        active_engagements=5,
        success_rate=99.5
    ),
    CyberAgent(
        name="RedTeam Agent",
        icon="⚔️",
        description="Autonomous penetration testing across kill chain",
        capabilities=["Reconnaissance", "Weaponization", "Delivery", "Exploitation"],
        tools_available=52,
        active_engagements=2,
        success_rate=98.9
    ),
    CyberAgent(
        name="Malware Agent",
        icon="🦠",
        description="Reverse engineering and malware analysis",
        capabilities=["Static analysis", "Dynamic analysis", "YARA rules", "Sandbox execution"],
        tools_available=8,
        active_engagements=1,
        success_rate=99.2
    ),
    CyberAgent(
        name="Security Agent",
        icon="🔐",
        description="Threat detection and pattern matching",
        capabilities=["Pattern matching", "IOC search", "SIEM queries", "Auto-response"],
        tools_available=10,
        active_engagements=7,
        success_rate=99.9
    ),
    CyberAgent(
        name="CloudSecurity Agent",
        icon="☁️",
        description="Multi-cloud security posture management",
        capabilities=["AWS CSPM", "Azure Security", "GCP scanning", "Compliance"],
        tools_available=18,
        active_engagements=4,
        success_rate=99.6
    ),
]

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

# =============================================================================
# API Routes
# =============================================================================

@app.get("/")
async def root():
    """Dashboard landing page"""
    return HTMLResponse(content=open("frontend/dist/index.html").read())

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "agents_loaded": len(AGENTS)
    }

@app.get("/api/agents", response_model=Dict[str, AgentStatus])
async def get_agents():
    """Get all agent statuses"""
    return AGENTS

@app.get("/api/agents/{agent_id}", response_model=AgentStatus)
async def get_agent(agent_id: str):
    """Get specific agent details"""
    if agent_id not in AGENTS:
        raise HTTPException(status_code=404, detail="Agent not found")
    return AGENTS[agent_id]

@app.get("/api/cyber-agents", response_model=List[CyberAgent])
async def get_cyber_agents():
    """Get all Cyber Division agents"""
    return CYBER_AGENTS

@app.get("/api/cyber-agents/{agent_id}", response_model=CyberAgent)
async def get_cyber_agent(agent_id: str):
    """Get specific Cyber Division agent"""
    # Support multiple key formats: "soc", "socagent", "SOC Agent"
    agent_map = {}
    for agent in CYBER_AGENTS:
        # Short key: "soc"
        short_key = agent.name.lower().replace("agent", "").replace(" ", "")
        # Full key: "socagent"
        full_key = agent.name.lower().replace(" ", "")
        # Name key: "soc agent"
        name_key = agent.name.lower()
        agent_map[short_key] = agent
        agent_map[full_key] = agent
        agent_map[name_key] = agent
    
    if agent_id not in agent_map:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent_map[agent_id]

@app.get("/api/metrics", response_model=LiveMetrics)
async def get_metrics():
    """Get live system metrics"""
    total_requests = sum(agent.requests_per_minute for agent in AGENTS.values())
    active_agents = sum(1 for agent in AGENTS.values() if agent.status == "online")
    avg_latency = sum(agent.avg_latency_ms for agent in AGENTS.values()) / len(AGENTS)
    avg_success = sum(agent.success_rate for agent in AGENTS.values()) / len(AGENTS)
    
    return LiveMetrics(
        total_requests=total_requests,
        active_agents=active_agents,
        avg_latency=avg_latency,
        error_rate=100 - avg_success,
        requests_per_second=total_requests / 60
    )

@app.get("/api/metrics/history/{metric_type}")
async def get_metrics_history(metric_type: str, points: int = 50):
    """Get historical metrics for graphs"""
    now = datetime.utcnow()
    history = []
    
    for i in range(points):
        timestamp = (now.timestamp() - (points - i) * 60) * 1000
        # Simulate realistic metric data
        if metric_type == "requests":
            value = random.randint(150, 300)
        elif metric_type == "latency":
            value = random.uniform(30, 100)
        elif metric_type == "errors":
            value = random.uniform(0, 2)
        elif metric_type == "agents":
            value = 6
        else:
            value = 0
            
        history.append({"timestamp": str(int(timestamp)), "value": value})
    
    return history

@app.get("/api/demos/chaos")
async def get_chaos_demo():
    """Get chaos engineering demo data"""
    return {
        "experiments": [
            {
                "name": "Agent Failure Injection",
                "status": "running",
                "target": "SOC Agent",
                "started": "2026-04-18T10:30:00Z",
                "duration": "15 minutes",
                "resiliency_score": 98.5
            },
            {
                "name": "Database Latency Test",
                "status": "completed",
                "target": "PostgreSQL",
                "started": "2026-04-18T09:00:00Z",
                "duration": "30 minutes",
                "resiliency_score": 99.2
            },
            {
                "name": "Network Partition",
                "status": "scheduled",
                "target": "Redis Cluster",
                "started": "2026-04-18T14:00:00Z",
                "duration": "20 minutes",
                "resiliency_score": None
            }
        ],
        "overall_resiliency": 98.8,
        "total_experiments": 15,
        "success_rate": 93.3
    }

@app.get("/api/examples/kaliagent")
async def get_kaliagent_examples():
    """Get KaliAgent usage examples"""
    return {
        "examples": [
            {
                "name": "External Reconnaissance",
                "description": "Scan external target for open ports and services",
                "playbook": "recon",
                "tools": ["Nmap", "Amass", "theHarvester", "Shodan", "Maltego"],
                "duration": "45-90 minutes",
                "authorization": "BASIC"
            },
            {
                "name": "Web Application Audit",
                "description": "Test web application for OWASP Top 10 vulnerabilities",
                "playbook": "web_audit",
                "tools": ["SQLMap", "Nikto", "Gobuster", "BurpSuite", "WPScan"],
                "duration": "60-120 minutes",
                "authorization": "ADVANCED"
            },
            {
                "name": "Password Cracking",
                "description": "Test password strength and crack hashes",
                "playbook": "password_audit",
                "tools": ["John", "Hashcat", "Hydra", "Medusa"],
                "duration": "30 minutes - 24 hours",
                "authorization": "ADVANCED"
            }
        ],
        "total_playbooks": 5,
        "total_tools": 52
    }

# =============================================================================
# WebSocket for Real-time Updates
# =============================================================================

@app.websocket("/ws/metrics")
async def websocket_metrics(websocket: WebSocket):
    """WebSocket endpoint for real-time metrics streaming"""
    await manager.connect(websocket)
    try:
        while True:
            # Send live metrics every 2 seconds
            metrics = await get_metrics()
            await websocket.send_json({
                "type": "metrics",
                "data": metrics.dict()
            })
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.websocket("/ws/agents")
async def websocket_agents(websocket: WebSocket):
    """WebSocket endpoint for real-time agent status updates"""
    await manager.connect(websocket)
    try:
        while True:
            # Send agent status every 5 seconds
            agents_data = {
                agent_id: agent.dict()
                for agent_id, agent in AGENTS.items()
            }
            await websocket.send_json({
                "type": "agents",
                "data": agents_data
            })
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# =============================================================================
# Background Tasks for Live Data
# =============================================================================

async def update_agent_metrics():
    """Periodically update agent metrics with realistic variations"""
    while True:
        for agent in AGENTS.values():
            # Simulate realistic metric fluctuations
            agent.requests_per_minute = max(50, agent.requests_per_minute + random.randint(-20, 20))
            agent.avg_latency_ms = max(10, agent.avg_latency_ms + random.uniform(-5, 5))
            agent.success_rate = min(100, max(95, agent.success_rate + random.uniform(-0.1, 0.1)))
            agent.last_active = datetime.utcnow().isoformat()
        
        await asyncio.sleep(10)

@app.on_event("startup")
async def startup_event():
    """Start background tasks on server startup"""
    asyncio.create_task(update_agent_metrics())

# =============================================================================
# Main Entry Point
# =============================================================================

if __name__ == "__main__":
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║   Agentic AI Dashboard v2.0 - Professional Server         ║")
    print("║   Live Graphs | Interactive Agents | Cyber Division      ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    print("")
    print("🚀 Starting server...")
    print("📊 API Docs: http://localhost:8002/docs")
    print("🎯 Dashboard: http://localhost:8002")
    print("📡 WebSocket: ws://localhost:8002/ws/metrics")
    print("")
    
    uvicorn.run(app, host="0.0.0.0", port=8002)
