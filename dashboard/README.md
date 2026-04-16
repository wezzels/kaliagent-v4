# Agentic AI Dashboard

**Real-time monitoring and management dashboard for Agentic AI system.**

---

## Features

- 📊 **Agent Status Overview** - Real-time status of all 10 agents
- 🔐 **Security Monitoring** - Live threat detection, incidents, vulnerabilities
- 🚀 **DevOps Dashboard** - Deployments, pipelines, infrastructure, alerts
- 📈 **Data Analytics** - Dataset statistics, trends, anomalies
- 🎫 **Support Tickets** - Ticket queue, SLA tracking, satisfaction scores
- 🤖 **Agent Orchestration** - Lead Agent task delegation and workflows

---

## Quick Start

### Option 1: Development Server

```bash
cd dashboard
npm install
npm run dev
```

Open http://localhost:3000

### Option 2: Production Build

```bash
npm run build
npm run preview
```

---

## API Endpoints

The dashboard connects to the Agentic AI API:

```
GET  /api/v1/status          # System status
GET  /api/v1/agents          # List all agents
GET  /api/v1/security/state  # Security agent state
GET  /api/v1/devops/state    # DevOps agent state
GET  /api/v1/data/state      # Data analyst state
GET  /api/v1/support/state   # Support agent state
```

---

## Components

### Security Dashboard
- Real-time threat detection
- Incident timeline
- Vulnerability scanner results
- Secrets rotation status
- Compliance metrics

### DevOps Dashboard
- Active deployments
- Pipeline status
- Infrastructure resources
- Cost tracking
- Monitoring alerts

### Data Analytics Dashboard
- Dataset overview
- Statistical analysis
- Trend detection
- Anomaly alerts
- Generated reports

### Support Dashboard
- Ticket queue
- SLA compliance
- Satisfaction scores
- Knowledge base stats
- Auto-response tracking

---

## Configuration

Create `.env.local`:

```env
VITE_API_URL=http://localhost:5000
VITE_REFRESH_INTERVAL=30000
VITE_THEME=dark
```

---

## Tech Stack

- **Frontend:** React 18 + Vite
- **UI:** Tailwind CSS + shadcn/ui
- **Charts:** Recharts
- **State:** Zustand
- **HTTP:** Axios

---

## Development

```bash
# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run linter
npm run lint
```

---

## Screenshots

### Overview Dashboard
Shows all agents, system health, and key metrics.

### Security Dashboard  
Real-time threat detection, incident management, vulnerability scanning.

### DevOps Dashboard
Deployments, CI/CD pipelines, infrastructure monitoring.

### Support Dashboard
Ticket management, SLA tracking, customer satisfaction.

---

## License

MIT
