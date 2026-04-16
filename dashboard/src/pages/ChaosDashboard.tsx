import React, { useState } from 'react';
import { 
  Play, 
  Pause, 
  StopCircle, 
  Plus, 
  Filter, 
  TrendingUp, 
  AlertCircle,
  CheckCircle,
  XCircle,
  Clock,
  Target,
  Shield,
  Activity
} from 'lucide-react';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  Legend
} from 'recharts';

// Mock data - would come from API
const mockExperiments = [
  {
    id: 'exp-2026041612345678',
    name: 'Instance Termination Test',
    type: 'instance_termination',
    status: 'completed',
    severity: 'medium',
    blastRadius: 'limited',
    targets: 2,
    duration: 15,
    startedAt: '2026-04-16T14:30:00Z',
    completedAt: '2026-04-16T14:45:00Z',
    outcome: 'System recovered in 3 minutes',
  },
  {
    id: 'exp-2026041612345679',
    name: 'Latency Injection - API Service',
    type: 'latency_injection',
    status: 'running',
    severity: 'low',
    blastRadius: 'single',
    targets: 1,
    duration: 30,
    startedAt: '2026-04-16T15:00:00Z',
    completedAt: null,
    outcome: null,
  },
  {
    id: 'exp-2026041612345680',
    name: 'Network Partition Test',
    type: 'network_partition',
    status: 'scheduled',
    severity: 'high',
    blastRadius: 'moderate',
    targets: 3,
    duration: 45,
    startedAt: null,
    completedAt: null,
    outcome: null,
  },
  {
    id: 'exp-2026041612345681',
    name: 'Database Failover',
    type: 'database_failure',
    status: 'aborted',
    severity: 'critical',
    blastRadius: 'limited',
    targets: 1,
    duration: 5,
    startedAt: '2026-04-16T13:00:00Z',
    completedAt: '2026-04-16T13:05:00Z',
    outcome: 'Aborted: Availability threshold breached',
  },
];

const mockMetrics = [
  { time: '14:30', errorRate: 0.5, latency: 120, availability: 99.9 },
  { time: '14:32', errorRate: 0.8, latency: 135, availability: 99.8 },
  { time: '14:34', errorRate: 1.2, latency: 145, availability: 99.7 },
  { time: '14:36', errorRate: 1.5, latency: 140, availability: 99.6 },
  { time: '14:38', errorRate: 1.0, latency: 130, availability: 99.7 },
  { time: '14:40', errorRate: 0.6, latency: 125, availability: 99.8 },
  { time: '14:42', errorRate: 0.4, latency: 120, availability: 99.9 },
  { time: '14:44', errorRate: 0.3, latency: 118, availability: 99.95 },
];

const mockResiliencyScores = [
  { service: 'web-api', score: 87, availability: 92, recovery: 85, degradation: 80, monitoring: 90 },
  { service: 'ml-inference', score: 92, availability: 95, recovery: 90, degradation: 88, monitoring: 95 },
  { service: 'payment-service', score: 78, availability: 80, recovery: 75, degradation: 70, monitoring: 85 },
  { service: 'user-auth', score: 95, availability: 98, recovery: 93, degradation: 92, monitoring: 97 },
];

const statusColors: Record<string, string> = {
  completed: 'bg-green-100 text-green-800',
  running: 'bg-blue-100 text-blue-800',
  scheduled: 'bg-slate-100 text-slate-800',
  aborted: 'bg-red-100 text-red-800',
  failed: 'bg-orange-100 text-orange-800',
};

const severityColors: Record<string, string> = {
  low: 'bg-blue-100 text-blue-700',
  medium: 'bg-amber-100 text-amber-700',
  high: 'bg-orange-100 text-orange-700',
  critical: 'bg-red-100 text-red-700',
};

const COLORS = ['#22c55e', '#3b82f6', '#f59e0b', '#ef4444'];

export default function ChaosDashboard() {
  const [selectedExperiment, setSelectedExperiment] = useState<string | null>(null);
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [experiments, setExperiments] = useState(mockExperiments);
  const [metrics, setMetrics] = useState(mockMetrics);
  const [resiliencyScores, setResiliencyScores] = useState(mockResiliencyScores);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch real data from API
  React.useEffect(() => {
    const fetchData = async () => {
      try {
        const chaosRes = await fetch('/api/demo/chaos');
        if (chaosRes.ok) {
          const data = await chaosRes.json();
          if (data.experiments) setExperiments(data.experiments);
          if (data.metrics) setMetrics(data.metrics);
          if (data.resiliencyScores) setResiliencyScores(data.resiliencyScores);
        }
        setError(null);
      } catch (err) {
        setError('Failed to load chaos data - using mock data');
        console.error('Error fetching chaos data:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const filteredExperiments = filterStatus === 'all' 
    ? experiments 
    : experiments.filter(e => e.status === filterStatus);

  const runningExperiment = experiments.find(e => e.status === 'running');

  return (
    <div className="space-y-6">
      {/* Error Banner */}
      {error && (
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 flex items-center gap-3">
          <AlertCircle className="w-5 h-5 text-amber-600" />
          <p className="text-amber-800 text-sm">{error}</p>
        </div>
      )}

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Chaos Monkey Dashboard</h1>
          <p className="text-slate-600 mt-1">Monitor and manage chaos engineering experiments</p>
        </div>
        <button className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">
          <Plus className="w-5 h-5" />
          New Experiment
        </button>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-6 rounded-xl border border-slate-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-slate-600">Total Experiments</p>
              <p className="text-2xl font-bold text-slate-900 mt-1">47</p>
            </div>
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <Activity className="w-6 h-6 text-blue-600" />
            </div>
          </div>
          <p className="text-sm text-green-600 mt-2 flex items-center gap-1">
            <TrendingUp className="w-4 h-4" />
            +12 this month
          </p>
        </div>

        <div className="bg-white p-6 rounded-xl border border-slate-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-slate-600">Running</p>
              <p className="text-2xl font-bold text-slate-900 mt-1">
                {mockExperiments.filter(e => e.status === 'running').length}
              </p>
            </div>
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
              <Play className="w-6 h-6 text-green-600" />
            </div>
          </div>
          <p className="text-sm text-slate-500 mt-2">Active now</p>
        </div>

        <div className="bg-white p-6 rounded-xl border border-slate-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-slate-600">Success Rate</p>
              <p className="text-2xl font-bold text-slate-900 mt-1">89.4%</p>
            </div>
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
              <CheckCircle className="w-6 h-6 text-green-600" />
            </div>
          </div>
          <p className="text-sm text-green-600 mt-2">Last 30 days</p>
        </div>

        <div className="bg-white p-6 rounded-xl border border-slate-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-slate-600">Avg Resiliency</p>
              <p className="text-2xl font-bold text-slate-900 mt-1">88.0</p>
            </div>
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
              <Shield className="w-6 h-6 text-purple-600" />
            </div>
          </div>
          <p className="text-sm text-slate-500 mt-2">Across all services</p>
        </div>
      </div>

      {/* Real-time Metrics (if experiment running) */}
      {runningExperiment && (
        <div className="bg-white p-6 rounded-xl border border-slate-200">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
              <h2 className="text-lg font-semibold text-slate-900">
                Live: {runningExperiment.name}
              </h2>
            </div>
            <button className="flex items-center gap-2 text-red-600 hover:text-red-700">
              <StopCircle className="w-5 h-5" />
              Abort Experiment
            </button>
          </div>

          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={mockMetrics}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis yAxisId="left" />
                <YAxis yAxisId="right" orientation="right" />
                <Tooltip />
                <Legend />
                <Line yAxisId="left" type="monotone" dataKey="errorRate" stroke="#ef4444" name="Error Rate %" />
                <Line yAxisId="right" type="monotone" dataKey="latency" stroke="#3b82f6" name="Latency (ms)" />
                <Line yAxisId="right" type="monotone" dataKey="availability" stroke="#22c55e" name="Availability %" />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <div className="grid grid-cols-3 gap-4 mt-4">
            <div className="bg-red-50 p-3 rounded-lg">
              <p className="text-sm text-red-600">Current Error Rate</p>
              <p className="text-xl font-bold text-red-700">0.3%</p>
              <p className="text-xs text-red-600 mt-1">Threshold: 2.0%</p>
            </div>
            <div className="bg-blue-50 p-3 rounded-lg">
              <p className="text-sm text-blue-600">P99 Latency</p>
              <p className="text-xl font-bold text-blue-700">118ms</p>
              <p className="text-xs text-blue-600 mt-1">Threshold: 500ms</p>
            </div>
            <div className="bg-green-50 p-3 rounded-lg">
              <p className="text-sm text-green-600">Availability</p>
              <p className="text-xl font-bold text-green-700">99.95%</p>
              <p className="text-xs text-green-600 mt-1">Threshold: 99.0%</p>
            </div>
          </div>
        </div>
      )}

      {/* Resiliency Scores */}
      <div className="bg-white p-6 rounded-xl border border-slate-200">
        <h2 className="text-lg font-semibold text-slate-900 mb-4">Service Resiliency Scores</h2>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={mockResiliencyScores}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="service" />
              <YAxis domain={[0, 100]} />
              <Tooltip />
              <Legend />
              <Bar dataKey="score" fill="#3b82f6" name="Overall Score" />
              <Bar dataKey="availability" fill="#22c55e" name="Availability" />
              <Bar dataKey="recovery" fill="#f59e0b" name="Recovery" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Experiments List */}
      <div className="bg-white rounded-xl border border-slate-200">
        <div className="p-6 border-b border-slate-200 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-slate-900">Experiments</h2>
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-slate-400" />
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="border border-slate-300 rounded-lg px-3 py-1.5 text-sm"
            >
              <option value="all">All Status</option>
              <option value="running">Running</option>
              <option value="completed">Completed</option>
              <option value="scheduled">Scheduled</option>
              <option value="aborted">Aborted</option>
              <option value="failed">Failed</option>
            </select>
          </div>
        </div>

        <table className="w-full">
          <thead className="bg-slate-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                Experiment
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                Type
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                Severity
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                Targets
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                Duration
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200">
            {filteredExperiments.map((exp) => (
              <tr key={exp.id} className="hover:bg-slate-50">
                <td className="px-6 py-4">
                  <div>
                    <p className="font-medium text-slate-900">{exp.name}</p>
                    <p className="text-sm text-slate-500">{exp.id}</p>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <span className="text-sm text-slate-600">{exp.type.replace(/_/g, ' ')}</span>
                </td>
                <td className="px-6 py-4">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${statusColors[exp.status]}`}>
                    {exp.status === 'running' && <Play className="w-3 h-3 mr-1" />}
                    {exp.status === 'completed' && <CheckCircle className="w-3 h-3 mr-1" />}
                    {exp.status === 'aborted' && <XCircle className="w-3 h-3 mr-1" />}
                    {exp.status === 'scheduled' && <Clock className="w-3 h-3 mr-1" />}
                    {exp.status}
                  </span>
                </td>
                <td className="px-6 py-4">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${severityColors[exp.severity]}`}>
                    {exp.severity}
                  </span>
                </td>
                <td className="px-6 py-4">
                  <div className="flex items-center gap-1 text-sm text-slate-600">
                    <Target className="w-4 h-4" />
                    {exp.targets}
                  </div>
                </td>
                <td className="px-6 py-4">
                  <span className="text-sm text-slate-600">{exp.duration} min</span>
                </td>
                <td className="px-6 py-4">
                  <button 
                    onClick={() => setSelectedExperiment(exp.id)}
                    className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                  >
                    View Details
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
