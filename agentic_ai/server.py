#!/usr/bin/env python3
"""
Agentic AI - API Server
=======================

Production REST API server with FastAPI.
"""

import os
import logging
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agentic_ai.collaboration.workspace import Workspace
from agentic_ai.collaboration.sessions import SessionManager, CollaborationSession
from agentic_ai.collaboration.presence import CollaborationHub
from agentic_ai.monitoring.metrics import MetricsRegistry

# Note: LeadAgent and other agents are available but not instantiated by default
# Import as needed: from agentic_ai.agents.lead import LeadAgent


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
    description="Multi-Agent Orchestration Framework",
    version="0.7.0",
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

# Initialize components
session_manager = SessionManager()
collaboration_hub = CollaborationHub()
metrics = MetricsRegistry()
# lead_agent = LeadAgent()  # Uncomment when LeadAgent is available

# In-memory workspace store (replace with persistent storage in production)
workspaces = {}


# ============================================
# Pydantic Models
# ============================================

class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str
    timestamp: str


class WorkspaceCreate(BaseModel):
    name: str
    creator_id: str


class WorkspaceResponse(BaseModel):
    workspace_id: str
    name: str
    creator_id: str
    participant_count: int
    resource_count: int


class SessionCreate(BaseModel):
    name: str
    creator_id: str


class SessionResponse(BaseModel):
    session_id: str
    name: str
    status: str
    creator_id: str
    participant_count: int


class AgentTaskRequest(BaseModel):
    task: str
    agent_type: Optional[str] = "developer"
    priority: Optional[int] = 5


class AgentTaskResponse(BaseModel):
    task_id: str
    status: str
    agent_type: str
    created_at: str


# ============================================
# Health & Status Endpoints
# ============================================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Basic health check endpoint."""
    return HealthResponse(
        status="healthy",
        version="0.7.0",
        environment=ENV,
        timestamp=datetime.utcnow().isoformat(),
    )


@app.get("/ready")
async def readiness_check():
    """Readiness probe - checks dependencies."""
    # Check Redis connection (if configured)
    redis_host = os.getenv("REDIS_HOST", "localhost")
    
    # Check database
    # In production, verify actual connectivity
    
    return {"status": "ready", "redis_host": redis_host}


@app.get("/metrics")
async def get_metrics():
    """Prometheus metrics endpoint."""
    # In production, this would expose Prometheus format
    state = metrics.get_state()
    return {
        "agents_total": state.get("agents_total", 0),
        "sessions_active": state.get("sessions_active", 0),
        "operations_total": state.get("operations_total", 0),
    }


@app.get("/api/v1/status")
async def get_status():
    """Application status overview."""
    return {
        "version": "0.7.0",
        "environment": ENV,
        "active_sessions": session_manager.get_state()["active_sessions"],
        "online_users": len(collaboration_hub.presence.get_online_users()),
        "metrics": metrics.get_state(),
    }


# ============================================
# Workspace Endpoints
# ============================================

@app.post("/api/v1/workspaces", response_model=WorkspaceResponse)
async def create_workspace(workspace_data: WorkspaceCreate):
    """Create a new workspace."""
    workspace = Workspace(name=workspace_data.name)
    workspace.add_participant(workspace_data.creator_id, is_owner=True)
    
    workspaces[workspace.workspace_id] = workspace
    
    logger.info(f"Created workspace: {workspace.workspace_id}")
    
    return WorkspaceResponse(
        workspace_id=workspace.workspace_id,
        name=workspace.name,
        creator_id=workspace_data.creator_id,
        participant_count=1,
        resource_count=0,
    )


@app.get("/api/v1/workspaces/{workspace_id}")
async def get_workspace(workspace_id: str):
    """Get workspace details."""
    if workspace_id not in workspaces:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    workspace = workspaces[workspace_id]
    return {
        "workspace_id": workspace.workspace_id,
        "name": workspace.name,
        "participants": len(workspace.participants),
        "resources": len(workspace.resources),
    }


# ============================================
# Session Endpoints
# ============================================

@app.post("/api/v1/sessions", response_model=SessionResponse)
async def create_session(session_data: SessionCreate):
    """Create a new collaboration session."""
    session = session_manager.create_session(
        name=session_data.name,
        creator_id=session_data.creator_id,
    )
    session.start()
    
    logger.info(f"Created session: {session.session_id}")
    
    return SessionResponse(
        session_id=session.session_id,
        name=session.name,
        status=session.status.value,
        creator_id=session_data.creator_id,
        participant_count=1,
    )


@app.post("/api/v1/sessions/{session_id}/join")
async def join_session(session_id: str, user_id: str, name: str):
    """Join an existing session."""
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    participant = session.join(user_id=user_id, name=name)
    collaboration_hub.presence.mark_active(user_id, session_id=session_id)
    
    return {
        "session_id": session_id,
        "participant_id": participant.participant_id,
        "user_id": user_id,
        "role": participant.role.value,
    }


@app.get("/api/v1/sessions/{session_id}")
async def get_session(session_id: str):
    """Get session details."""
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "session_id": session.session_id,
        "name": session.name,
        "status": session.status.value,
        "participants": session.get_active_participant_count(),
        "created_at": session.created_at,
    }


# ============================================
# Agent Endpoints
# ============================================

@app.post("/api/v1/agents/tasks", response_model=AgentTaskResponse)
async def create_agent_task(task_data: AgentTaskRequest, background_tasks: BackgroundTasks):
    """Create a task for an agent."""
    task_id = f"task-{datetime.utcnow().timestamp()}"
    
    # In production, this would queue the task for async execution
    background_tasks.add_task(
        execute_agent_task,
        task_id,
        task_data.task,
        task_data.agent_type,
    )
    
    return AgentTaskResponse(
        task_id=task_id,
        status="queued",
        agent_type=task_data.agent_type,
        created_at=datetime.utcnow().isoformat(),
    )


async def execute_agent_task(task_id: str, task: str, agent_type: str):
    """Execute agent task in background."""
    logger.info(f"Executing task {task_id} for {agent_type} agent")
    
    # In production, route to appropriate agent
    # For now, just log
    pass


# ============================================
# Presence Endpoints
# ============================================

@app.get("/api/v1/presence")
async def get_presence():
    """Get all online users."""
    online = collaboration_hub.presence.get_online_users()
    return {
        "total": len(online),
        "users": [
            {
                "user_id": u.user_id,
                "status": u.status.value,
                "session_id": u.session_id,
            }
            for u in online
        ],
    }


@app.post("/api/v1/presence/{user_id}/active")
async def mark_active(user_id: str, session_id: Optional[str] = None):
    """Mark user as active."""
    collaboration_hub.presence.mark_active(user_id, session_id=session_id)
    return {"user_id": user_id, "status": "active"}


@app.post("/api/v1/presence/{user_id}/offline")
async def mark_offline(user_id: str):
    """Mark user as offline."""
    collaboration_hub.presence.set_offline(user_id)
    return {"user_id": user_id, "status": "offline"}


# ============================================
# Main Entry Point
# ============================================

def main():
    """Run the server."""
    import uvicorn
    
    host = os.getenv("AGENTIC_AI_HOST", "0.0.0.0")
    port = int(os.getenv("AGENTIC_AI_PORT", "5000"))
    
    logger.info(f"Starting Agentic AI server on {host}:{port}")
    logger.info(f"Environment: {ENV}")
    logger.info(f"Log level: {LOG_LEVEL}")
    
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
