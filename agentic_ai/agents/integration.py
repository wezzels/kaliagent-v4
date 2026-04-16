"""
IntegrationAgent - API & System Integrations
=============================================

Provides API connection management, webhook handling, data synchronization,
integration monitoring, and cross-platform automation.
"""

import logging
import secrets
import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Callable
import json


logger = logging.getLogger(__name__)


class ConnectionStatus(Enum):
    """Connection status states."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    RATE_LIMITED = "rate_limited"
    AUTH_EXPIRED = "auth_expired"


class SyncDirection(Enum):
    """Sync direction."""
    UNIDIRECTIONAL = "unidirectional"
    BIDIRECTIONAL = "bidirectional"
    PUSH_ONLY = "push_only"
    PULL_ONLY = "pull_only"


class WebhookEvent(Enum):
    """Webhook event types."""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    SYNC = "sync"
    ERROR = "error"
    CUSTOM = "custom"


@dataclass
class APIConnection:
    """API connection configuration."""
    connection_id: str
    name: str
    service: str
    base_url: str
    auth_type: str  # api_key, oauth2, basic, bearer
    status: ConnectionStatus
    api_key: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_expires: Optional[datetime] = None
    rate_limit: int = 1000
    rate_limit_remaining: int = 1000
    rate_limit_reset: Optional[datetime] = None
    last_used: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Webhook:
    """Webhook configuration."""
    webhook_id: str
    name: str
    url: str
    events: List[WebhookEvent]
    status: str  # active, paused, disabled
    secret: str
    connection_id: Optional[str] = None
    last_triggered: Optional[datetime] = None
    success_count: int = 0
    failure_count: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SyncJob:
    """Data synchronization job."""
    job_id: str
    name: str
    source_connection: str
    target_connection: str
    direction: SyncDirection
    schedule: str  # cron expression or interval
    status: str  # pending, running, completed, failed
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    records_synced: int = 0
    errors: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class IntegrationLog:
    """Integration activity log."""
    log_id: str
    integration_type: str  # connection, webhook, sync
    entity_id: str
    action: str
    status: str
    details: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)


class IntegrationAgent:
    """
    Integration Agent for API connections, webhooks,
    data synchronization, and cross-platform automation.
    """
    
    def __init__(self, agent_id: str = "integration-agent"):
        self.agent_id = agent_id
        self.connections: Dict[str, APIConnection] = {}
        self.webhooks: Dict[str, Webhook] = {}
        self.sync_jobs: Dict[str, SyncJob] = {}
        self.logs: List[IntegrationLog] = []
        
        # Pre-built service templates
        self.service_templates = self._init_service_templates()
    
    def _init_service_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize service connection templates."""
        return {
            'slack': {
                'name': 'Slack',
                'base_url': 'https://slack.com/api',
                'auth_type': 'bearer',
                'endpoints': {'post_message': '/chat.postMessage', 'get_channels': '/conversations.list'},
            },
            'github': {
                'name': 'GitHub',
                'base_url': 'https://api.github.com',
                'auth_type': 'bearer',
                'endpoints': {'repos': '/user/repos', 'issues': '/repos/{owner}/{repo}/issues'},
            },
            'salesforce': {
                'name': 'Salesforce',
                'base_url': 'https://api.salesforce.com/services/data/v58.0',
                'auth_type': 'oauth2',
                'endpoints': {'accounts': '/sobjects/Account', 'contacts': '/sobjects/Contact'},
            },
            'hubspot': {
                'name': 'HubSpot',
                'base_url': 'https://api.hubapi.com',
                'auth_type': 'api_key',
                'endpoints': {'contacts': '/crm/v3/objects/contacts', 'companies': '/crm/v3/objects/companies'},
            },
            'stripe': {
                'name': 'Stripe',
                'base_url': 'https://api.stripe.com/v1',
                'auth_type': 'bearer',
                'endpoints': {'charges': '/charges', 'customers': '/customers'},
            },
            'sendgrid': {
                'name': 'SendGrid',
                'base_url': 'https://api.sendgrid.com/v3',
                'auth_type': 'api_key',
                'endpoints': {'send': '/mail/send', 'templates': '/templates'},
            },
            'twilio': {
                'name': 'Twilio',
                'base_url': 'https://api.twilio.com/2010-04-01',
                'auth_type': 'basic',
                'endpoints': {'messages': '/Accounts/{sid}/Messages.json'},
            },
            'google': {
                'name': 'Google APIs',
                'base_url': 'https://www.googleapis.com',
                'auth_type': 'oauth2',
                'endpoints': {'sheets': '/sheets/v4/spreadsheets', 'drive': '/drive/v3/files'},
            },
        }
    
    # ============================================
    # API Connection Management
    # ============================================
    
    def create_connection(
        self,
        name: str,
        service: str,
        auth_type: str,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        access_token: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> APIConnection:
        """Create a new API connection."""
        # Use template if available
        template = self.service_templates.get(service.lower(), {})
        
        connection = APIConnection(
            connection_id=self._generate_id("conn"),
            name=name,
            service=service,
            base_url=base_url or template.get('base_url', ''),
            auth_type=auth_type,
            status=ConnectionStatus.ACTIVE,
            api_key=api_key,
            access_token=access_token,
            config=config or {},
        )
        
        self.connections[connection.connection_id] = connection
        self._log('connection', connection.connection_id, 'created', 'success')
        
        logger.info(f"Created connection: {connection.name} ({connection.service})")
        return connection
    
    def test_connection(self, connection_id: str) -> Dict[str, Any]:
        """Test API connection."""
        if connection_id not in self.connections:
            return {'success': False, 'error': 'Connection not found'}
        
        conn = self.connections[connection_id]
        
        # Simulate connection test
        result = {
            'success': True,
            'connection_id': connection_id,
            'service': conn.service,
            'latency_ms': 45,  # Simulated
            'authenticated': conn.access_token or conn.api_key is not None,
            'rate_limit': conn.rate_limit,
        }
        
        conn.last_used = datetime.utcnow()
        self._log('connection', connection_id, 'test', 'success', result)
        
        return result
    
    def update_connection_status(
        self,
        connection_id: str,
        status: ConnectionStatus,
        error: Optional[str] = None,
    ) -> bool:
        """Update connection status."""
        if connection_id not in self.connections:
            return False
        
        conn = self.connections[connection_id]
        conn.status = status
        
        if error:
            self._log('connection', connection_id, 'error', 'error', {'error': error})
        
        return True
    
    def get_connections(self, status: Optional[ConnectionStatus] = None) -> List[APIConnection]:
        """Get connections with filtering."""
        connections = list(self.connections.values())
        
        if status:
            connections = [c for c in connections if c.status == status]
        
        return connections
    
    def remove_connection(self, connection_id: str) -> bool:
        """Remove a connection."""
        if connection_id not in self.connections:
            return False
        
        del self.connections[connection_id]
        self._log('connection', connection_id, 'removed', 'success')
        
        return True
    
    # ============================================
    # Webhook Management
    # ============================================
    
    def create_webhook(
        self,
        name: str,
        url: str,
        events: List[WebhookEvent],
        connection_id: Optional[str] = None,
        secret: Optional[str] = None,
    ) -> Webhook:
        """Create a new webhook."""
        webhook = Webhook(
            webhook_id=self._generate_id("webhook"),
            name=name,
            url=url,
            events=events,
            status="active",
            secret=secret or self._generate_secret(),
            connection_id=connection_id,
        )
        
        self.webhooks[webhook.webhook_id] = webhook
        self._log('webhook', webhook.webhook_id, 'created', 'success')
        
        logger.info(f"Created webhook: {webhook.name} -> {webhook.url}")
        return webhook
    
    def trigger_webhook(
        self,
        webhook_id: str,
        event: WebhookEvent,
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Trigger a webhook."""
        if webhook_id not in self.webhooks:
            return {'success': False, 'error': 'Webhook not found'}
        
        webhook = self.webhooks[webhook_id]
        
        if webhook.status != 'active':
            return {'success': False, 'error': f'Webhook is {webhook.status}'}
        
        if event not in webhook.events and WebhookEvent.CUSTOM not in webhook.events:
            return {'success': False, 'error': f'Event {event} not subscribed'}
        
        # Simulate webhook delivery
        webhook.last_triggered = datetime.utcnow()
        webhook.success_count += 1
        
        result = {
            'success': True,
            'webhook_id': webhook_id,
            'delivered_at': webhook.last_triggered.isoformat(),
            'payload_size': len(json.dumps(payload)),
        }
        
        self._log('webhook', webhook_id, 'triggered', 'success', {'event': event.value})
        
        return result
    
    def pause_webhook(self, webhook_id: str) -> bool:
        """Pause a webhook."""
        if webhook_id not in self.webhooks:
            return False
        
        self.webhooks[webhook_id].status = 'paused'
        return True
    
    def get_webhooks(self, status: Optional[str] = None) -> List[Webhook]:
        """Get webhooks with filtering."""
        webhooks = list(self.webhooks.values())
        
        if status:
            webhooks = [w for w in webhooks if w.status == status]
        
        return webhooks
    
    # ============================================
    # Sync Job Management
    # ============================================
    
    def create_sync_job(
        self,
        name: str,
        source_connection: str,
        target_connection: str,
        direction: SyncDirection,
        schedule: str,
    ) -> SyncJob:
        """Create a data synchronization job."""
        job = SyncJob(
            job_id=self._generate_id("sync"),
            name=name,
            source_connection=source_connection,
            target_connection=target_connection,
            direction=direction,
            schedule=schedule,
            status="pending",
        )
        
        self.sync_jobs[job.job_id] = job
        self._log('sync', job.job_id, 'created', 'success')
        
        logger.info(f"Created sync job: {job.name}")
        return job
    
    def run_sync_job(self, job_id: str, records: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Execute a sync job."""
        if job_id not in self.sync_jobs:
            return {'success': False, 'error': 'Job not found'}
        
        job = self.sync_jobs[job_id]
        job.status = 'running'
        job.last_run = datetime.utcnow()
        
        # Simulate sync
        record_count = len(records) if records else 100
        job.records_synced += record_count
        job.status = 'completed'
        
        result = {
            'success': True,
            'job_id': job_id,
            'records_synced': record_count,
            'duration_ms': 1250,  # Simulated
        }
        
        self._log('sync', job_id, 'executed', 'success', {'records': record_count})
        
        return result
    
    def get_sync_jobs(self, status: Optional[str] = None) -> List[SyncJob]:
        """Get sync jobs with filtering."""
        jobs = list(self.sync_jobs.values())
        
        if status:
            jobs = [j for j in jobs if j.status == status]
        
        return jobs
    
    # ============================================
    # Integration Logs
    # ============================================
    
    def _log(
        self,
        integration_type: str,
        entity_id: str,
        action: str,
        status: str,
        details: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
    ):
        """Log integration activity."""
        log = IntegrationLog(
            log_id=self._generate_id("log"),
            integration_type=integration_type,
            entity_id=entity_id,
            action=action,
            status=status,
            details=details or {},
            error=error,
        )
        
        self.logs.append(log)
        
        # Keep last 10000 logs
        if len(self.logs) > 10000:
            self.logs = self.logs[-10000:]
    
    def get_logs(
        self,
        integration_type: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
    ) -> List[IntegrationLog]:
        """Get integration logs."""
        logs = self.logs
        
        if integration_type:
            logs = [l for l in logs if l.integration_type == integration_type]
        
        if status:
            logs = [l for l in logs if l.status == status]
        
        return logs[-limit:]
    
    # ============================================
    # Integration Health
    # ============================================
    
    def get_integration_health(self) -> Dict[str, Any]:
        """Get overall integration health summary."""
        connections = list(self.connections.values())
        webhooks = list(self.webhooks.values())
        sync_jobs = list(self.sync_jobs.values())
        
        active_connections = len([c for c in connections if c.status == ConnectionStatus.ACTIVE])
        active_webhooks = len([w for w in webhooks if w.status == 'active'])
        completed_syncs = len([j for j in sync_jobs if j.status == 'completed'])
        
        recent_errors = len([l for l in self.logs[-100:] if l.status == 'error'])
        
        return {
            'connections': {
                'total': len(connections),
                'active': active_connections,
                'error': len([c for c in connections if c.status == ConnectionStatus.ERROR]),
            },
            'webhooks': {
                'total': len(webhooks),
                'active': active_webhooks,
                'total_deliveries': sum(w.success_count for w in webhooks),
            },
            'sync_jobs': {
                'total': len(sync_jobs),
                'total_records': sum(j.records_synced for j in sync_jobs),
                'completed': completed_syncs,
            },
            'recent_errors': recent_errors,
            'health_score': self._calculate_health_score(active_connections, len(connections), recent_errors),
        }
    
    def _calculate_health_score(self, active: int, total: int, errors: int) -> float:
        """Calculate integration health score (0-100)."""
        if total == 0:
            return 100.0
        
        connection_score = (active / total) * 100
        error_penalty = min(errors * 5, 50)  # Max 50 point penalty
        
        return max(0, connection_score - error_penalty)
    
    # ============================================
    # Utilities
    # ============================================
    
    def _generate_id(self, prefix: str) -> str:
        """Generate a unique ID."""
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        random_suffix = secrets.token_hex(4)
        return f"{prefix}-{timestamp}-{random_suffix}"
    
    def _generate_secret(self) -> str:
        """Generate a webhook secret."""
        return secrets.token_urlsafe(32)
    
    def get_state(self) -> Dict[str, Any]:
        """Get agent state summary."""
        return {
            'agent_id': self.agent_id,
            'connections_count': len(self.connections),
            'active_connections': len([c for c in self.connections.values() if c.status == ConnectionStatus.ACTIVE]),
            'webhooks_count': len(self.webhooks),
            'sync_jobs_count': len(self.sync_jobs),
            'total_logs': len(self.logs),
        }


def get_capabilities() -> Dict[str, Any]:
    """Return agent capabilities for orchestration."""
    return {
        'agent_type': 'integration',
        'version': '1.0.0',
        'capabilities': [
            'create_connection',
            'test_connection',
            'update_connection_status',
            'get_connections',
            'remove_connection',
            'create_webhook',
            'trigger_webhook',
            'pause_webhook',
            'get_webhooks',
            'create_sync_job',
            'run_sync_job',
            'get_sync_jobs',
            'get_logs',
            'get_integration_health',
        ],
        'connection_statuses': [s.value for s in ConnectionStatus],
        'sync_directions': [d.value for d in SyncDirection],
        'webhook_events': [e.value for e in WebhookEvent],
        'service_templates': list(IntegrationAgent(None).service_templates.keys()),
    }


if __name__ == "__main__":
    agent = IntegrationAgent()
    
    # Create connection
    conn = agent.create_connection(
        name="Slack Bot",
        service="slack",
        auth_type="bearer",
        access_token="xoxb-xxx",
    )
    
    print(f"Created connection: {conn.name}")
    print(f"Service: {conn.service}")
    
    # Test connection
    result = agent.test_connection(conn.connection_id)
    print(f"Test result: {result['success']}")
    
    # Create webhook
    webhook = agent.create_webhook(
        name="GitHub Issues",
        url="https://api.example.com/webhooks/github",
        events=[WebhookEvent.CREATE, WebhookEvent.UPDATE],
    )
    
    print(f"\nCreated webhook: {webhook.name}")
    
    # Trigger webhook
    trigger = agent.trigger_webhook(
        webhook.webhook_id,
        WebhookEvent.CREATE,
        {'issue': 'test'},
    )
    print(f"Triggered: {trigger['success']}")
    
    # Create sync job
    sync = agent.create_sync_job(
        name="HubSpot to Salesforce",
        source_connection="hubspot",
        target_connection="salesforce",
        direction=SyncDirection.UNIDIRECTIONAL,
        schedule="0 */6 * * *",
    )
    
    print(f"\nCreated sync job: {sync.name}")
    
    # Health check
    health = agent.get_integration_health()
    print(f"\nHealth Score: {health['health_score']}")
    
    print(f"\nState: {agent.get_state()}")
