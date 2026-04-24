# KaliAgent v4 - API Documentation

**Version:** 4.0.0  
**Base URL:** `http://localhost:5007/api`

---

## Table of Contents

1. [Authentication](#authentication)
2. [Health & Status](#health--status)
3. [Scanning](#scanning)
4. [Attacks](#attacks)
5. [C2 Management](#c2-management)
6. [AI Features](#ai-features)
7. [Reporting](#reporting)
8. [System](#system)

---

## Authentication

Most endpoints require authentication via API key:

```bash
curl -H "X-API-Key: your-api-key" http://localhost:5007/api/...
```

---

## Health & Status

### GET /health

Check system health.

**Response:**
```json
{
  "status": "healthy",
  "version": "4.0.0",
  "timestamp": "2026-04-24T06:00:00Z",
  "services": {
    "dashboard": "running",
    "c2_servers": "active",
    "database": "connected",
    "redis": "connected"
  }
}
```

### GET /status

Get detailed system status.

**Response:**
```json
{
  "uptime": 86400,
  "active_attacks": 2,
  "registered_agents": 5,
  "reports_generated": 12
}
```

---

## Scanning

### POST /scan

Initiate a network scan.

**Request:**
```json
{
  "target": "10.0.100.0/24",
  "scan_type": "nmap",
  "options": ["-sV", "-O", "-A"]
}
```

**Response:**
```json
{
  "scan_id": "scan_12345",
  "status": "started",
  "estimated_duration": 300
}
```

### GET /scan/{scan_id}

Get scan status and results.

**Response:**
```json
{
  "scan_id": "scan_12345",
  "status": "completed",
  "progress": 100,
  "results": {
    "hosts": 5,
    "open_ports": 23,
    "vulnerabilities": 12,
    "services": [...]
  }
}
```

---

## Attacks

### POST /attack

Launch an automated attack.

**Request:**
```json
{
  "target": "10.0.100.10",
  "attack_type": "web",
  "method": "sql_injection",
  "auto_exploit": true
}
```

**Response:**
```json
{
  "attack_id": "attack_67890",
  "status": "running",
  "steps": [
    {"name": "Reconnaissance", "status": "completed"},
    {"name": "Vulnerability Detection", "status": "running"},
    {"name": "Exploitation", "status": "pending"}
  ]
}
```

### GET /attack/{attack_id}

Get attack status and results.

**Response:**
```json
{
  "attack_id": "attack_67890",
  "status": "completed",
  "success": true,
  "findings": [
    {
      "title": "SQL Injection",
      "severity": "Critical",
      "cvss": 9.8,
      "evidence": "admin'-- bypassed login"
    }
  ],
  "evidence_files": ["/app/evidence/screenshot_001.png"]
}
```

### POST /attack/{attack_id}/stop

Stop a running attack.

**Response:**
```json
{
  "status": "stopped",
  "reason": "user_requested"
}
```

---

## C2 Management

### GET /c2/agents

List all registered C2 agents.

**Response:**
```json
{
  "agents": [
    {
      "agent_id": "agent-001",
      "c2_type": "sliver",
      "ip": "10.0.100.10",
      "os": "windows",
      "status": "active",
      "last_seen": "2026-04-24T05:55:00Z"
    }
  ]
}
```

### POST /c2/register

Register a new C2 agent.

**Request:**
```json
{
  "c2_type": "sliver",
  "agent_id": "agent-002",
  "metadata": {
    "hostname": "target-pc",
    "os": "linux",
    "user": "admin"
  }
}
```

**Response:**
```json
{
  "status": "registered",
  "agent_id": "agent-002"
}
```

### POST /c2/{agent_id}/command

Execute command on agent.

**Request:**
```json
{
  "command": "whoami",
  "timeout": 30
}
```

**Response:**
```json
{
  "output": "nt authority\\system",
  "exit_code": 0,
  "execution_time": 0.5
}
```

---

## AI Features

### POST /ai/analyze

Analyze scan results with LLM.

**Request:**
```json
{
  "nmap_output": "PORT STATE SERVICE\n22/tcp open ssh\n80/tcp open http",
  "request": "Identify vulnerabilities and recommend attacks"
}
```

**Response:**
```json
{
  "analysis": {
    "summary": "Target running SSH and Apache web server",
    "vulnerabilities": [
      {
        "service": "Apache",
        "risk": "High",
        "recommendation": "Check version for known CVEs"
      }
    ],
    "attack_vectors": [
      "SQL injection on web server",
      "SSH brute force"
    ]
  }
}
```

### POST /ai/parse-command

Parse natural language command.

**Request:**
```json
{
  "command": "Scan the 10.0.100.0/24 network for web servers"
}
```

**Response:**
```json
{
  "type": "scan",
  "target": "10.0.100.0/24",
  "scan_type": "nmap",
  "options": ["-p 80,443", "--script http-enum"]
}
```

### POST /ai/chat

Chat with AI assistant.

**Request:**
```json
{
  "message": "What's the best exploit for Apache 2.4.18?",
  "context": "Target is Ubuntu 16.04"
}
```

**Response:**
```json
{
  "response": "Apache 2.4.18 has several known vulnerabilities...",
  "confidence": 0.92,
  "sources": ["CVE-2016-2161", "CVE-2016-5384"]
}
```

---

## Reporting

### POST /report/generate

Generate penetration test report.

**Request:**
```json
{
  "results": {
    "client": "Example Corp",
    "findings": [...],
    "executive_summary": "..."
  },
  "format": "pdf"
}
```

**Response:**
```json
{
  "status": "success",
  "file_path": "/app/reports/pentest_report_20260424.pdf",
  "download_url": "http://localhost:5007/reports/pentest_report_20260424.pdf"
}
```

### GET /reports

List all generated reports.

**Response:**
```json
{
  "reports": [
    {
      "filename": "pentest_report_20260424.pdf",
      "format": "pdf",
      "size": 524288,
      "created_at": "2026-04-24T06:00:00Z"
    }
  ]
}
```

---

## System

### GET /stats

Get system statistics.

**Response:**
```json
{
  "cpu_usage": 23.5,
  "memory_usage": 45.2,
  "disk_usage": 67.8,
  "network_rx": 1024.5,
  "network_tx": 512.3
}
```

### GET /attacks/history

Get attack history.

**Query Parameters:**
- `limit` (default: 10)
- `offset` (default: 0)
- `status` (optional: completed, running, failed)

**Response:**
```json
{
  "attacks": [
    {
      "attack_id": "attack_67890",
      "target": "10.0.100.10",
      "type": "web",
      "status": "completed",
      "success": true,
      "duration": 120,
      "created_at": "2026-04-24T05:00:00Z"
    }
  ],
  "total": 42,
  "limit": 10,
  "offset": 0
}
```

---

## Error Responses

All errors follow this format:

```json
{
  "error": {
    "code": "SCAN_FAILED",
    "message": "Scan failed: target unreachable",
    "details": {...}
  }
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `UNAUTHORIZED` | 401 | Invalid or missing API key |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `SCAN_FAILED` | 400 | Scan execution failed |
| `ATTACK_FAILED` | 400 | Attack execution failed |
| `RATE_LIMITED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Server error |

---

## Rate Limiting

- Default: 100 requests per minute per API key
- Scan endpoints: 10 requests per minute
- Attack endpoints: 5 requests per minute

Rate limit headers:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1682352000
```

---

## WebSocket API

Real-time updates via WebSocket:

```javascript
const socket = io('http://localhost:5007');

// Subscribe to scan updates
socket.on('scan_update', (data) => {
  console.log('Scan progress:', data.progress);
});

// Subscribe to attack updates
socket.on('attack_update', (data) => {
  console.log('Attack step:', data.step);
});

// Subscribe to terminal output
socket.on('terminal_output', (data) => {
  console.log('Terminal:', data.message);
});
```

---

**🍀 Happy Hacking!**
