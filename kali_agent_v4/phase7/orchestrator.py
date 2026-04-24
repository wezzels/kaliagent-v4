#!/usr/bin/env python3
"""
KaliAgent v4 - Phase 7: Lead Agent Orchestrator
Coordinates multiple agents for large-scale operations
"""

import json
import time
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from enum import Enum

from .agent_base import AgentBase, AgentRole, AgentStatus, Task, Intelligence, AgentState


class OperationStatus(Enum):
    """Operation status"""
    PLANNING = "planning"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Operation:
    """Multi-agent operation"""
    operation_id: str
    name: str
    description: str
    target: str
    status: str = "planning"
    lead_agent: Optional[str] = None
    team_agents: List[str] = field(default_factory=list)
    tasks: List[Task] = field(default_factory=list)
    intelligence: List[Intelligence] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    progress: float = 0.0
    findings: Dict[str, Any] = field(default_factory=dict)


class LeadAgent:
    """
    Lead Agent - Orchestrates multi-agent operations
    
    Responsibilities:
    - Team formation
    - Task decomposition
    - Resource allocation
    - Progress monitoring
    - Intelligence aggregation
    - Result synthesis
    """
    
    def __init__(self, host: str = "localhost", port: int = 5007):
        self.agent_id = f"lead-{uuid.uuid4().hex[:8]}"
        self.host = host
        self.port = port
        self.role = AgentRole.LEAD
        self.registered_agents: Dict[str, AgentBase] = {}
        self.active_operations: Dict[str, Operation] = {}
        self.intelligence_hub: List[Intelligence] = []
        self.operation_templates = self._load_templates()
        
        print(f"🍀 Lead Agent initialized: {self.agent_id}")
    
    def _load_templates(self) -> Dict:
        """Load operation templates"""
        return {
            "web_assessment": {
                "description": "Complete web application security assessment",
                "phases": [
                    {"name": "Reconnaissance", "agent_role": "scout", "duration": 300},
                    {"name": "Scanning", "agent_role": "scout", "duration": 600},
                    {"name": "Exploitation", "agent_role": "attacker", "duration": 900},
                    {"name": "Reporting", "agent_role": "reporter", "duration": 300}
                ]
            },
            "network_pentest": {
                "description": "Full network penetration test",
                "phases": [
                    {"name": "Network Discovery", "agent_role": "scout", "duration": 600},
                    {"name": "Service Enumeration", "agent_role": "scout", "duration": 900},
                    {"name": "Vulnerability Analysis", "agent_role": "analyst", "duration": 600},
                    {"name": "Exploitation", "agent_role": "attacker", "duration": 1200},
                    {"name": "Lateral Movement", "agent_role": "attacker", "duration": 900},
                    {"name": "Reporting", "agent_role": "reporter", "duration": 600}
                ]
            },
            "wifi_audit": {
                "description": "WiFi security audit",
                "phases": [
                    {"name": "WiFi Survey", "agent_role": "specialist", "duration": 300},
                    {"name": "Target Selection", "agent_role": "analyst", "duration": 60},
                    {"name": "Handshake Capture", "agent_role": "specialist", "duration": 1800},
                    {"name": "Cracking", "agent_role": "specialist", "duration": 3600},
                    {"name": "Reporting", "agent_role": "reporter", "duration": 300}
                ]
            }
        }
    
    def register_agent(self, agent: AgentBase):
        """Register an agent with the lead"""
        self.registered_agents[agent.agent_id] = agent
        print(f"✅ Agent registered: {agent.agent_id} ({agent.role.value})")
    
    def create_operation(self, template_name: str, target: str, name: str = None) -> Operation:
        """Create operation from template"""
        if template_name not in self.operation_templates:
            raise ValueError(f"Unknown template: {template_name}")
        
        template = self.operation_templates[template_name]
        
        operation = Operation(
            operation_id=f"op-{uuid.uuid4().hex[:8]}",
            name=name or f"{template_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            description=template["description"],
            target=target,
            lead_agent=self.agent_id
        )
        
        # Decompose into tasks
        operation.tasks = self._decompose_to_tasks(template, target)
        
        # Form team
        operation.team_agents = self._form_team(template)
        
        self.active_operations[operation.operation_id] = operation
        print(f"🎯 Operation created: {operation.operation_id} ({operation.name})")
        print(f"   Target: {target}")
        print(f"   Team: {len(operation.team_agents)} agents")
        print(f"   Tasks: {len(operation.tasks)}")
        
        return operation
    
    def _decompose_to_tasks(self, template: Dict, target: str) -> List[Task]:
        """Decompose operation into tasks"""
        tasks = []
        
        for i, phase in enumerate(template["phases"]):
            task = Task(
                task_id=f"task-{uuid.uuid4().hex[:8]}",
                task_type=phase["name"].lower().replace(" ", "_"),
                description=phase["name"],
                target=target,
                priority=10 - i,  # Earlier phases have higher priority
                parameters={"phase": i, "duration": phase["duration"]}
            )
            tasks.append(task)
        
        return tasks
    
    def _form_team(self, template: Dict) -> List[str]:
        """Form agent team based on operation requirements"""
        required_roles = set(phase["agent_role"] for phase in template["phases"])
        team = []
        
        for agent_id, agent in self.registered_agents.items():
            if agent.role.value in required_roles:
                team.append(agent_id)
        
        # If missing roles, note it
        available_roles = set(self.registered_agents[a].role.value for a in team)
        missing = required_roles - available_roles
        
        if missing:
            print(f"⚠️  Missing roles: {missing}")
        
        return team
    
    def start_operation(self, operation_id: str) -> bool:
        """Start an operation"""
        if operation_id not in self.active_operations:
            return False
        
        operation = self.active_operations[operation_id]
        operation.status = "running"
        operation.started_at = datetime.utcnow().isoformat()
        
        print(f"🚀 Starting operation: {operation.name}")
        
        # Assign tasks to agents
        self._assign_tasks(operation)
        
        return True
    
    def _assign_tasks(self, operation: Operation):
        """Assign tasks to team agents"""
        for task in operation.tasks:
            # Find best agent for this task
            best_agent = self._find_best_agent(task)
            
            if best_agent:
                task.assigned_to = best_agent
                agent = self.registered_agents[best_agent]
                agent.assign_task(task)
                print(f"   Task '{task.description}' → {best_agent}")
            else:
                print(f"   ⚠️  No agent available for '{task.description}'")
    
    def _find_best_agent(self, task: Task) -> Optional[str]:
        """Find best agent for a task"""
        candidates = []
        
        for agent_id, agent in self.registered_agents.items():
            if agent.status == AgentStatus.IDLE and agent._can_execute(task):
                candidates.append((agent_id, agent))
        
        if not candidates:
            return None
        
        # Pick agent with least current load
        return min(candidates, key=lambda x: len(x[1].task_queue))[0]
    
    def get_operation_status(self, operation_id: str) -> Dict:
        """Get operation status"""
        if operation_id not in self.active_operations:
            return {"error": "Operation not found"}
        
        operation = self.active_operations[operation_id]
        
        # Calculate progress
        total_tasks = len(operation.tasks)
        completed_tasks = sum(1 for t in operation.tasks if t.status == "completed")
        operation.progress = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        # Check if complete
        if completed_tasks == total_tasks:
            operation.status = "completed"
            operation.completed_at = datetime.utcnow().isoformat()
        
        return {
            "operation_id": operation.operation_id,
            "name": operation.name,
            "status": operation.status,
            "progress": operation.progress,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "team_size": len(operation.team_agents),
            "findings": operation.findings
        }
    
    def aggregate_intelligence(self, operation_id: str) -> Dict:
        """Aggregate intelligence from all agents"""
        if operation_id not in self.active_operations:
            return {}
        
        operation = self.active_operations[operation_id]
        aggregated = {
            "hosts": [],
            "services": [],
            "vulnerabilities": [],
            "credentials": [],
            "networks": []
        }
        
        # Collect from all team agents
        for agent_id in operation.team_agents:
            agent = self.registered_agents.get(agent_id)
            if agent:
                intel = agent.query_intelligence()
                for item in intel:
                    if item.intel_type in aggregated:
                        aggregated[item.intel_type].append(asdict(item))
        
        operation.intelligence = [Intelligence(**i) for i in aggregated.values() if i]
        operation.findings = aggregated
        
        return aggregated
    
    def pause_operation(self, operation_id: str) -> bool:
        """Pause an operation"""
        if operation_id not in self.active_operations:
            return False
        
        operation = self.active_operations[operation_id]
        operation.status = "paused"
        
        # Pause all agent tasks
        for agent_id in operation.team_agents:
            agent = self.registered_agents.get(agent_id)
            if agent and agent.current_task:
                agent.status = AgentStatus.WAITING
        
        print(f"⏸️  Operation paused: {operation.name}")
        return True
    
    def resume_operation(self, operation_id: str) -> bool:
        """Resume a paused operation"""
        if operation_id not in self.active_operations:
            return False
        
        operation = self.active_operations[operation_id]
        if operation.status != "paused":
            return False
        
        operation.status = "running"
        
        # Resume all agent tasks
        for agent_id in operation.team_agents:
            agent = self.registered_agents.get(agent_id)
            if agent and agent.status == AgentStatus.WAITING:
                agent.status = AgentStatus.BUSY
        
        print(f"▶️  Operation resumed: {operation.name}")
        return True
    
    def terminate_operation(self, operation_id: str) -> bool:
        """Terminate an operation"""
        if operation_id not in self.active_operations:
            return False
        
        operation = self.active_operations[operation_id]
        operation.status = "failed"
        operation.completed_at = datetime.utcnow().isoformat()
        
        # Stop all agent tasks
        for agent_id in operation.team_agents:
            agent = self.registered_agents.get(agent_id)
            if agent:
                agent.current_task = None
                agent.status = AgentStatus.IDLE
        
        print(f"🛑 Operation terminated: {operation.name}")
        return True
    
    def get_team_status(self) -> List[Dict]:
        """Get status of all registered agents"""
        return [agent.heartbeat() for agent in self.registered_agents.values()]
    
    def generate_report(self, operation_id: str) -> Dict:
        """Generate operation report"""
        if operation_id not in self.active_operations:
            return {"error": "Operation not found"}
        
        operation = self.active_operations[operation_id]
        
        # Aggregate final intelligence
        self.aggregate_intelligence(operation_id)
        
        report = {
            "operation_id": operation.operation_id,
            "name": operation.name,
            "target": operation.target,
            "status": operation.status,
            "duration": operation.completed_at or "ongoing",
            "progress": operation.progress,
            "team": operation.team_agents,
            "tasks_completed": sum(1 for t in operation.tasks if t.status == "completed"),
            "total_tasks": len(operation.tasks),
            "findings_summary": {
                "hosts": len(operation.findings.get("hosts", [])),
                "vulnerabilities": len(operation.findings.get("vulnerabilities", [])),
                "credentials": len(operation.findings.get("credentials", []))
            }
        }
        
        return report


# Example usage
if __name__ == "__main__":
    # Create lead agent
    lead = LeadAgent(host="10.0.100.1")
    
    # Create team
    scout1 = AgentBase(AgentRole.SCOUT, host="10.0.100.2")
    scout2 = AgentBase(AgentRole.SCOUT, host="10.0.100.3")
    attacker1 = AgentBase(AgentRole.ATTACKER, host="10.0.100.4")
    analyst1 = AgentBase(AgentRole.ANALYST, host="10.0.100.5")
    reporter1 = AgentBase(AgentRole.REPORTER, host="10.0.100.6")
    
    # Register agents
    lead.register_agent(scout1)
    lead.register_agent(scout2)
    lead.register_agent(attacker1)
    lead.register_agent(analyst1)
    lead.register_agent(reporter1)
    
    # Create operation
    op = lead.create_operation(
        template_name="network_pentest",
        target="10.0.100.0/24",
        name="Q2_Network_Assessment"
    )
    
    # Start operation
    lead.start_operation(op.operation_id)
    
    # Monitor progress
    for _ in range(5):
        status = lead.get_operation_status(op.operation_id)
        print(f"\n📊 Progress: {status['progress']:.1f}%")
        time.sleep(1)
    
    # Generate report
    report = lead.generate_report(op.operation_id)
    print(f"\n📄 Operation Report:")
    print(json.dumps(report, indent=2))
