#!/usr/bin/env python3
"""
Agentic AI - Demo API Server
============================

Simple demo server for testing deployment.
"""

import os
import logging
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Configuration
LOG_LEVEL = os.getenv("AGENTIC_AI_LOG_LEVEL", "INFO")
ENV = os.getenv("AGENTIC_AI_ENV", "production")

# Setup logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("agentic_ai.server")

# Initialize FastAPI app
app = FastAPI(
    title="Agentic AI",
    description="Multi-Agent Orchestration Framework - Demo Server",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("Agentic AI server starting...")


# ============================================
# Pydantic Models
# ============================================

class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str
    timestamp: str
    agents_loaded: int


class AgentInfo(BaseModel):
    agent_id: str
    agent_type: str
    status: str


class AgentsResponse(BaseModel):
    agents: list[AgentInfo]
    total: int


# ============================================
# Health & Status Endpoints
# ============================================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Basic health check endpoint."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        environment=ENV,
        timestamp=datetime.utcnow().isoformat(),
        agents_loaded=33,
    )


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Agentic AI",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/api/agents", response_model=AgentsResponse)
async def get_agents():
    """List all available agents."""
    agent_types = [
        "base", "developer", "qa", "sysadmin", "lead",
        "sales", "finance", "hr", "marketing", "product",
        "research", "data_analyst", "data_governance",
        "devops", "support", "integration", "communications",
        "legal", "compliance", "privacy", "risk", "ethics",
        "security", "soc", "vulnman", "redteam", "malware", "cloud_security",
        "ml_ops", "supply_chain", "audit", "vendor_risk", "chaos_monkey",
    ]
    
    agents = [
        AgentInfo(
            agent_id=f"{agent_type}-1",
            agent_type=agent_type,
            status="healthy"
        )
        for agent_type in agent_types
    ]
    
    return AgentsResponse(agents=agents, total=len(agents))


@app.get("/api/agents/{agent_type}")
async def get_agent_info(agent_type: str):
    """Get info about a specific agent type."""
    return {
        "agent_type": agent_type,
        "status": "healthy",
        "capabilities": ["capability_1", "capability_2"],
    }


# ============================================
# Demo Data Endpoints (for dashboard testing)
# ============================================

@app.get("/api/demo/chaos")
async def get_demo_chaos():
    """Demo chaos data."""
    return {
        "experiments": [
            {"id": "exp-1", "name": "AZ Failure Test", "status": "completed", "success_rate": 0.95},
            {"id": "exp-2", "name": "Network Partition", "status": "running", "success_rate": None},
        ],
        "resiliency_score": 87.5,
    }


@app.get("/api/demo/vendors")
async def get_demo_vendors():
    """Demo vendor data."""
    return {
        "vendors": [
            {"id": "v-1", "name": "CloudProvider Inc", "tier": "tier_1", "risk_score": 0.45},
            {"id": "v-2", "name": "DataCorp", "tier": "tier_2", "risk_score": 0.32},
        ],
        "total": 2,
    }


@app.get("/api/demo/audits")
async def get_demo_audits():
    """Demo audit data."""
    return {
        "audits": [
            {"id": "a-1", "title": "SOC2 2026", "status": "in_progress", "findings": 5},
        ],
        "total": 1,
    }


# ============================================
# Main Entry Point
# ============================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "agentic_ai.server:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
    )
