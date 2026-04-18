# Agentic AI Dashboard v2.0 - Deployment Guide

**Professional monitoring dashboard for agents.bedimsecurity.com**

---

## 🚀 Quick Deploy

### Option 1: Direct Deployment (Recommended for Development)

```bash
# 1. Install backend dependencies
cd /home/wez/stsgym-work/agentic_ai/dashboard_v2/backend
pip install -r requirements.txt

# 2. Start backend server
python server.py &

# 3. Install frontend dependencies
cd ../frontend
npm install

# 4. Start frontend dev server
npm run dev

# 5. Open browser
# http://localhost:5173
```

### Option 2: Docker Deployment (Production)

```bash
# Build and run with Docker Compose
cd /home/wez/stsgym-work/agentic_ai/dashboard_v2
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Option 3: Deploy to agents.bedimsecurity.com

```bash
# SSH to server
ssh crackers@wezzel.com -p 23 -i ~/.openclaw/workspace/crackers

# Create deployment directory
sudo mkdir -p /opt/agentic-dashboard
sudo chown crackers:crackers /opt/agentic-dashboard
cd /opt/agentic-dashboard

# Clone repository
git clone https://idm.wezzel.com/crab-meat-repos/stsgym-work.git .
cd agentic_ai/dashboard_v2

# Install dependencies
pip install -r backend/requirements.txt
cd frontend && npm install && npm run build

# Create systemd service
sudo nano /etc/systemd/system/agentic-dashboard.service
```

**Systemd Service Configuration:**

```ini
[Unit]
Description=Agentic AI Dashboard v2.0
After=network.target

[Service]
Type=simple
User=crackers
WorkingDirectory=/opt/agentic-dashboard/agentic_ai/dashboard_v2/backend
ExecStart=/opt/agentic-dashboard/agentic_ai/venv/bin/python server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable agentic-dashboard
sudo systemctl start agentic-dashboard
sudo systemctl status agentic-dashboard

# Configure nginx
sudo nano /etc/nginx/conf.d/agents.conf
```

**Nginx Configuration:**

```nginx
server {
    listen 443 ssl;
    server_name agents.bedimsecurity.com;

    ssl_certificate /etc/letsencrypt/live/bedimsecurity.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/bedimsecurity.com/privkey.pem;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Frontend static files
    location / {
        root /opt/agentic-dashboard/agentic_ai/dashboard_v2/frontend/dist;
        try_files $uri $uri/ /index.html;
        expires 1h;
        add_header Cache-Control "public, immutable";
    }

    # Backend API proxy
    location /api {
        proxy_pass http://127.0.0.1:8002;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # WebSocket support
    location /ws {
        proxy_pass http://127.0.0.1:8002;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400;
    }
}

# HTTP redirect
server {
    listen 80;
    server_name agents.bedimsecurity.com;
    return 301 https://$server_name$request_uri;
}
```

```bash
# Test nginx config
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx

# Get SSL certificate (if not already done)
sudo certbot --nginx -d agents.bedimsecurity.com

# Verify deployment
curl https://agents.bedimsecurity.com/api/health
```

---

## 📊 Architecture

```
┌─────────────────────────────────────────────────────────┐
│              agents.bedimsecurity.com                   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐     ┌──────────────┐                │
│  │  React 18    │────▶│  FastAPI     │                │
│  │  Frontend    │◀───▶│  Backend     │                │
│  │  (Port 5173) │ WS  │  (Port 8002) │                │
│  └──────────────┘     └──────┬───────┘                │
│                              │                         │
│              ┌───────────────┼───────────────┐        │
│              │               │               │        │
│              ▼               ▼               ▼        │
│       ┌──────────┐   ┌──────────┐   ┌──────────┐    │
│       │PostgreSQL│   │  Redis   │   │WebSocket │    │
│       │ Database │   │  Cache   │   │  Server  │    │
│       └──────────┘   └──────────┘   └──────────┘    │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 🔧 Configuration

### Environment Variables

Create `.env` file in backend directory:

```bash
# Server Configuration
DASHBOARD_PORT=8002
DASHBOARD_HOST=0.0.0.0
LOG_LEVEL=INFO

# API Configuration
API_VERSION=2.0.0
ENABLE_WEBSOCKET=true
WEBSOCKET_UPDATE_INTERVAL=2000

# Cyber Division Configuration
CYBER_AGENTS_ENABLED=true
KALIAGENT_INTEGRATION=true

# Security (for production)
CORS_ORIGINS=https://agents.bedimsecurity.com
SECRET_KEY=your-secret-key-here
```

---

## 📁 File Structure

```
dashboard_v2/
├── backend/
│   ├── server.py              # FastAPI backend with WebSocket
│   ├── requirements.txt       # Python dependencies
│   └── .env                   # Environment variables
├── frontend/
│   ├── src/
│   │   ├── App.tsx            # Main React component
│   │   ├── App.css            # Professional styles
│   │   ├── main.tsx           # Entry point
│   │   └── index.css          # Global styles
│   ├── public/
│   │   └── shield.svg         # Favicon
│   ├── index.html             # HTML template
│   ├── package.json           # Node dependencies
│   ├── vite.config.ts         # Vite configuration
│   └── tsconfig.json          # TypeScript config
├── tests/
│   ├── test_dashboard.py      # Backend tests
│   └── test_e2e.spec.ts       # Playwright E2E tests
├── docker-compose.yml         # Docker deployment
├── Dockerfile                 # Container build
├── DEPLOYMENT.md              # This file
├── README.md                  # Overview
└── DEVELOPMENT.md             # Development guide
```

---

## 🧪 Testing

### Backend Tests

```bash
cd backend
pip install -r requirements.txt
pytest -v
```

### Frontend Tests

```bash
cd frontend
npm install
npm run test
```

### E2E Tests

```bash
# Install Playwright
npx playwright install

# Run tests
npx playwright test
```

---

## 📈 Monitoring

### Health Check Endpoint

```bash
curl https://agents.bedimsecurity.com/api/health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "timestamp": "2026-04-18T21:30:00Z",
  "agents_loaded": 6
}
```

### Metrics Endpoint

```bash
curl https://agents.bedimsecurity.com/api/metrics
```

### Agent Status

```bash
curl https://agents.bedimsecurity.com/api/agents
curl https://agents.bedimsecurity.com/api/cyber-agents
```

---

## 🔐 Security Considerations

1. **SSL/TLS**: Always use HTTPS in production
2. **CORS**: Restrict origins to trusted domains
3. **WebSocket**: Implement authentication for production
4. **Rate Limiting**: Add rate limiting for API endpoints
5. **Environment Variables**: Never commit secrets to git

---

## 🚨 Troubleshooting

### Frontend won't build

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

### Backend won't start

```bash
cd backend
pip install -r requirements.txt
python server.py
```

### WebSocket not connecting

1. Check nginx WebSocket configuration
2. Verify firewall allows WebSocket connections
3. Check browser console for errors

### SSL certificate issues

```bash
sudo certbot renew
sudo systemctl reload nginx
```

---

## 📞 Support

- **Documentation**: https://agents.bedimsecurity.com/docs
- **GitHub**: https://github.com/wezzels/agentic-ai
- **Discord**: https://discord.gg/clawd

---

*Dashboard v2.0 - Built for Professional Security Operations*
