# Agentic AI Dashboard v2.0 - Development Guide

**For developers building on the dashboard platform**

---

## 🛠️ Development Environment Setup

### Prerequisites

- **Python 3.12+**
- **Node.js 20+**
- **npm 10+**
- **Git**

### Initial Setup

```bash
# Clone repository
cd /home/wez/stsgym-work/agentic_ai/dashboard_v2

# Create Python virtual environment
cd backend
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or: venv\Scripts\activate  # Windows

# Install Python dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd ../frontend
npm install
```

---

## 🚀 Development Workflow

### Start Backend Server

```bash
cd backend
source venv/bin/activate
python server.py
```

**Server will start at:** http://localhost:8002  
**API Docs:** http://localhost:8002/docs  
**WebSocket:** ws://localhost:8002/ws/metrics

### Start Frontend Dev Server

```bash
cd frontend
npm run dev
```

**Frontend will start at:** http://localhost:5173

Vite will automatically proxy API requests to the backend.

---

## 📝 Coding Standards

### Python (Backend)

Follow PEP 8 style guide:

```python
# Use type hints
def get_agent(agent_id: str) -> AgentStatus:
    ...

# Use docstrings
async def health_check():
    """Basic health check endpoint."""
    ...

# Use async/await for I/O
async def update_agent_metrics():
    ...
```

Run linting:

```bash
pip install flake8 black mypy
flake8 .
black .
mypy .
```

### TypeScript (Frontend)

Strict TypeScript configuration enabled:

```typescript
// Use interfaces for types
interface AgentStatus {
  name: string;
  status: string;
  capabilities: string[];
}

// Use functional components with hooks
function App() {
  const [metrics, setMetrics] = useState<LiveMetrics | null>(null);
  ...
}
```

Run linting:

```bash
npm run lint
```

---

## 🧪 Testing

### Backend Tests

```bash
cd backend
source venv/bin/activate
pytest tests/ -v --cov=.
```

**Test structure:**

```python
class TestAgentsEndpoints:
    """Test agent-related endpoints"""
    
    def test_get_all_agents(self):
        """Test getting all agents"""
        response = client.get("/api/agents")
        assert response.status_code == 200
```

### Frontend Tests

```bash
cd frontend
npm run test
```

### E2E Tests (Playwright)

```bash
# Install browsers
npx playwright install

# Run tests
npx playwright test

# Run with UI
npx playwright test --ui

# Generate report
npx playwright show-report
```

---

## 🔌 Adding New Agents

### Step 1: Add to Backend

Edit `backend/server.py`:

```python
AGENTS = {
    # ... existing agents ...
    "newagent": AgentStatus(
        name="New Agent",
        type="security",
        status="online",
        capabilities=["Capability 1", "Capability 2"],
        requests_per_minute=100,
        avg_latency_ms=50.0,
        success_rate=99.5,
        last_active=datetime.utcnow().isoformat()
    ),
}
```

### Step 2: Update Cyber Agents

```python
CYBER_AGENTS = [
    # ... existing agents ...
    CyberAgent(
        name="New Agent",
        icon="🆕",
        description="Description of the new agent",
        capabilities=["Cap 1", "Cap 2", "Cap 3"],
        tools_available=10,
        active_engagements=2,
        success_rate=99.0
    ),
]
```

### Step 3: Add Tests

Edit `tests/test_dashboard.py`:

```python
def test_new_agent(self):
    """Test new agent endpoint"""
    response = client.get("/api/agents/newagent")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Agent"
```

---

## 📊 Adding New Metrics

### Backend

Add new metric type to `get_metrics_history`:

```python
@app.get("/api/metrics/history/{metric_type}")
async def get_metrics_history(metric_type: str, points: int = 50):
    if metric_type == "new_metric":
        value = random.uniform(0, 100)  # Generate realistic data
```

### Frontend

Add new chart in `App.tsx`:

```tsx
<ResponsiveContainer width="100%" height={300}>
  <LineChart data={metricsHistory}>
    <Line type="monotone" dataKey="value" stroke="#3b82f6" />
  </LineChart>
</ResponsiveContainer>
```

---

## 🎨 Styling Guidelines

### Color Palette

Located in `frontend/src/index.css`:

```css
:root {
  --bg-primary: #0f172a;
  --bg-secondary: #1e293b;
  --primary: #3b82f6;
  --success: #10b981;
  --warning: #f59e0b;
  --danger: #ef4444;
}
```

### Component Structure

```tsx
<div className="component-container">
  <div className="component-header">
    <h2>Title</h2>
  </div>
  <div className="component-content">
    {/* Content */}
  </div>
</div>
```

### Responsive Design

Use CSS Grid and media queries:

```css
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1rem;
}

@media (max-width: 768px) {
  .grid {
    grid-template-columns: 1fr;
  }
}
```

---

## 🔌 WebSocket Integration

### Backend

```python
@app.websocket("/ws/custom")
async def websocket_custom(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.send_json({
                "type": "custom",
                "data": {"message": "Update"}
            })
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
```

### Frontend

```tsx
useEffect(() => {
  const ws = new WebSocket(`ws://${window.location.host}/ws/custom`);
  
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    // Handle update
  };
  
  return () => ws.close();
}, []);
```

---

## 📦 Building for Production

### Frontend Build

```bash
cd frontend
npm run build
```

Output: `frontend/dist/`

### Backend Package

```bash
cd backend
pip install -r requirements.txt
```

### Docker Build

```bash
docker-compose build
```

---

## 🐛 Debugging

### Backend Debugging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug("Debug message")
logger.info("Info message")
logger.error("Error message")
```

### Frontend Debugging

Open browser DevTools (F12):
- Console: View logs and errors
- Network: Monitor API calls
- Application: Check WebSocket connections

### WebSocket Debugging

```typescript
ws.onopen = () => console.log('WebSocket connected');
ws.onclose = () => console.log('WebSocket disconnected');
ws.onerror = (error) => console.error('WebSocket error:', error);
```

---

## 📈 Performance Optimization

### Backend

- Use async/await for I/O operations
- Cache frequently accessed data
- Use connection pooling for databases
- Implement rate limiting

### Frontend

- Use React.memo for expensive components
- Implement virtual scrolling for large lists
- Lazy load components with React.lazy
- Optimize images and assets

---

## 🔐 Security Best Practices

1. **Never commit secrets** - Use environment variables
2. **Validate all inputs** - Use Pydantic models
3. **Sanitize outputs** - Escape user-generated content
4. **Use HTTPS** - Always in production
5. **Implement authentication** - For sensitive endpoints
6. **Rate limit APIs** - Prevent abuse
7. **CORS configuration** - Restrict origins

---

## 📚 Resources

- **FastAPI Docs:** https://fastapi.tiangolo.com
- **React Docs:** https://react.dev
- **Recharts:** https://recharts.org
- **TypeScript:** https://typescriptlang.org
- **Vite:** https://vitejs.dev

---

## 🆘 Troubleshooting

### Backend won't start

```bash
# Check Python version
python --version  # Should be 3.12+

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check port availability
lsof -i :8002
```

### Frontend build fails

```bash
# Clear cache
rm -rf node_modules package-lock.json
npm install

# Check Node version
node --version  # Should be 20+
```

### WebSocket not connecting

1. Check backend is running
2. Verify firewall settings
3. Check browser console for errors
4. Test with: `curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" ws://localhost:8002/ws/metrics`

---

*Development Guide v2.0 - Last Updated: April 18, 2026*
