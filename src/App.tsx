import React, { useState, useEffect, useRef } from 'react';
import { 
  AlertCircle, 
  Activity, 
  Terminal, 
  MessageSquare, 
  Server, 
  Database, 
  Globe, 
  ShieldCheck,
  RefreshCw,
  Send,
  CheckCircle2,
  XCircle,
  Play
} from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  AreaChart,
  Area
} from 'recharts';
import { Observation, Action, ServiceState, TaskConfig } from './types';
export default function App() {
  const [tasks, setTasks] = useState<any[]>([]);
  const [currentTask, setCurrentTask] = useState<string>('task1');
  const [obs, setObs] = useState<Observation | null>(null);
  const [connectionError, setConnectionError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [aiRunning, setAiRunning] = useState(false);
  const [logs, setLogs] = useState<string[]>([]);
  const [selectedService, setSelectedService] = useState<string | null>(null);
  const [actionParams, setActionParams] = useState<string>('{}');
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const fetchTasks = async () => {
      try {
        setConnectionError(null);
        const res = await fetch('/api/tasks');
        if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
        const data = await res.json();
        setTasks(data.tasks || []);
      } catch (err) {
        console.error("Failed to fetch tasks:", err);
        setConnectionError("Backend connection failed. Please check if the server is running.");
        setLogs(prev => [...prev, `!! Error: Failed to fetch tasks. Backend might be offline.`]);
      }
    };
    fetchTasks();
    // Give backend time to start
    const timer = setTimeout(() => {
      handleReset('task1_easy');
    }, 1000);
    return () => clearTimeout(timer);
  }, []);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [obs?.recent_logs, logs]);

  const handleReset = async (taskId: string) => {
    setLoading(true);
    try {
      setConnectionError(null);
      const res = await fetch('/api/reset', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ task_id: taskId, seed: 42 })
      });
      if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
      const data = await res.json();
      setObs(data);
      setCurrentTask(taskId);
      setLogs([`> Environment reset for ${taskId}`]);
    } catch (err) {
      console.error("Failed to reset environment:", err);
      setConnectionError("Backend connection failed. Please check if the server is running.");
      setLogs(prev => [...prev, `!! Error: Failed to reset environment. Backend might be offline.`]);
    } finally {
      setLoading(false);
    }
  };

  const takeAction = async (action: Action) => {
    setLogs(prev => [...prev, `> Executing ${action.type} on ${action.target || 'system'}...`]);
    
    let finalParams = {};
    try {
      finalParams = JSON.parse(actionParams);
    } catch (e) {
      console.error("Invalid JSON in params", e);
    }

    try {
      const res = await fetch('/api/step', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...action, params: { ...action.params, ...finalParams } })
      });
      if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
      const data = await res.json();
      setObs(data.observation);
      setLogs(prev => [...prev, `< ${data.observation.action_feedback}`]);
    } catch (err) {
      console.error("Failed to execute action:", err);
      setLogs(prev => [...prev, `!! Error: Failed to execute action. Backend might be offline.`]);
    }
  };

  const handleRunBaseline = async () => {
    setLoading(true);
    setLogs(prev => [...prev, `> Running baseline agent...`]);
    const res = await fetch('/api/baseline', { method: 'POST' });
    const data = await res.json();
    setLogs(prev => [...prev, `> Baseline complete: Avg ${data.average}`]);
    setLoading(false);
  };

  const runAiAgent = async () => {
    if (!obs || aiRunning) return;
    setAiRunning(true);
    setLogs(prev => [...prev, `*** AI Agent securely starting investigation on backend... ***`]);

    try {
      const res = await fetch('/api/agent', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ observation: obs })
      });
      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.detail || `Server error ${res.status}`);
      }
      const data = await res.json();
      await takeAction(data.action || data);
    } catch (err: any) {
      console.error(err);
      setLogs(prev => [...prev, `!! AI Agent error: ${err.message}`]);
    } finally {
      setAiRunning(false);
    }
  };

  if (!obs) {
    return (
      <div className="flex flex-col items-center justify-center h-screen bg-black text-white gap-4">
        <div className="flex items-center gap-3">
          <RefreshCw className={`w-6 h-6 ${loading ? 'animate-spin' : ''} text-blue-500`} />
          <span className="text-xl font-bold tracking-tighter">INITIALIZING SIMULATION...</span>
        </div>
        {connectionError && (
          <div className="flex flex-col items-center gap-4 max-w-md text-center">
            <p className="text-red-400 text-sm bg-red-500/10 border border-red-500/20 p-4 rounded-lg">
              {connectionError}
            </p>
            <button 
              onClick={() => handleReset(currentTask || 'task1_easy')}
              className="px-6 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-md font-bold transition-all"
            >
              RETRY CONNECTION
            </button>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-gray-300 font-mono selection:bg-blue-500/30">
      {/* Header */}
      <header className="border-b border-white/10 bg-black/50 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-red-500/10 rounded-lg">
              <AlertCircle className="w-6 h-6 text-red-500" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-white tracking-tight">INCIDENT RESPONSE AI</h1>
              <p className="text-[10px] text-gray-500 uppercase tracking-widest">SRE Simulation Environment</p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <select 
              value={currentTask}
              onChange={(e) => handleReset(e.target.value)}
              className="bg-zinc-900 border border-white/10 rounded-md px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/50"
            >
              {tasks.map(t => (
                <option key={t.id} value={t.id}>{t.name} ({t.difficulty})</option>
              ))}
            </select>
            
            <button 
              onClick={handleRunBaseline}
              className="px-4 py-1.5 bg-purple-600/20 text-purple-400 border border-purple-500/30 rounded-md text-sm font-bold hover:bg-purple-600/30 transition-colors"
            >
              Run Baseline
            </button>

            <button 
              onClick={() => handleReset(currentTask)}
              className="p-2 hover:bg-white/5 rounded-md transition-colors"
              title="Reset Environment"
            >
              <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
            </button>

            <button 
              onClick={runAiAgent}
              disabled={aiRunning || obs.done}
              className="flex items-center gap-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white px-4 py-1.5 rounded-md text-sm font-bold transition-all shadow-lg shadow-blue-600/20"
            >
              <Play className="w-4 h-4 fill-current" />
              {aiRunning ? 'AI THINKING...' : 'RUN AI AGENT'}
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto p-6 grid grid-cols-12 gap-6">
        {/* Left Column: Metrics & Services */}
        <div className="col-span-12 lg:col-span-8 space-y-6">
          {/* Stats Bar */}
          <div className="grid grid-cols-4 gap-4">
            <StatCard label="SCORE" value={obs.score_so_far.toFixed(2)} color="text-blue-400" />
            <StatCard label="STEPS" value={`${obs.step_count}/${obs.max_steps}`} color="text-zinc-400" />
            <StatCard label="ALERTS" value={obs.active_alerts.length} color="text-red-400" />
            <StatCard label="TICKETS" value={obs.customer_tickets.filter(t => t.status === 'open').length} color="text-orange-400" />
          </div>

          {/* Services Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {Object.values(obs.services).map((service: ServiceState) => (
              <ServiceCard 
                key={service.name} 
                service={service} 
                isSelected={selectedService === service.name}
                onClick={() => { setSelectedService(service.name); }}
              />
            ))}
          </div>

          {/* Metrics Chart */}
          <div className="bg-zinc-900/50 border border-white/10 rounded-xl p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Activity className="w-4 h-4 text-blue-500" />
                SYSTEM METRICS {selectedService ? `(${selectedService.toUpperCase()})` : '(GLOBAL)'}
              </h3>
            </div>
            <div className="h-[300px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={generateChartData(obs.services)}>
                  <defs>
                    <linearGradient id="colorHealth" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#333" vertical={false} />
                  <XAxis dataKey="name" stroke="#666" fontSize={10} />
                  <YAxis stroke="#666" fontSize={10} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#18181b', border: '1px solid #333', fontSize: '12px' }}
                    itemStyle={{ color: '#fff' }}
                  />
                  <Area type="monotone" dataKey="health" stroke="#3b82f6" fillOpacity={1} fill="url(#colorHealth)" />
                  <Area type="monotone" dataKey="cpu" stroke="#ef4444" fill="transparent" />
                  <Area type="monotone" dataKey="memory" stroke="#10b981" fill="transparent" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Right Column: Console & Alerts */}
        <div className="col-span-12 lg:col-span-4 space-y-6">
          {/* Terminal Console */}
          <div className="bg-black border border-white/10 rounded-xl overflow-hidden flex flex-col h-[500px] shadow-2xl">
            <div className="bg-zinc-900 px-4 py-2 border-b border-white/10 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Terminal className="w-4 h-4 text-green-500" />
                <span className="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Operator Console</span>
              </div>
              <div className="flex gap-1.5">
                <div className="w-2 h-2 rounded-full bg-red-500/50" />
                <div className="w-2 h-2 rounded-full bg-yellow-500/50" />
                <div className="w-2 h-2 rounded-full bg-green-500/50" />
              </div>
            </div>
            <div 
              ref={scrollRef}
              className="flex-1 p-4 overflow-y-auto space-y-2 text-[12px] leading-relaxed"
            >
              {logs.map((log, i) => (
                <div key={i} className={log.startsWith('>') ? 'text-blue-400' : log.startsWith('!!') ? 'text-red-400' : 'text-gray-300'}>
                  {log}
                </div>
              ))}
              {obs.done && (
                <div className="mt-4 p-3 bg-green-500/10 border border-green-500/20 rounded-lg text-green-400 font-bold text-center">
                  MISSION COMPLETE | SCORE: {obs.score_so_far.toFixed(2)}
                </div>
              )}
            </div>
            <div className="p-4 border-t border-white/10 bg-zinc-900/50 space-y-4">
              <div className="space-y-2">
                <label className="text-[10px] font-bold text-gray-500 uppercase tracking-widest">Action Parameters (JSON)</label>
                <input 
                  type="text" 
                  value={actionParams}
                  onChange={(e) => setActionParams(e.target.value)}
                  placeholder='{"key": "value"}'
                  className="w-full bg-black border border-white/10 rounded-md px-3 py-2 text-xs font-mono focus:outline-none focus:ring-1 focus:ring-blue-500/50"
                />
              </div>
              <div className="grid grid-cols-2 gap-2">
                <ActionButton label="Check Logs" onClick={() => takeAction({ type: 'check_logs', target: selectedService, params: {} })} disabled={!selectedService} />
                <ActionButton label="Check Metrics" onClick={() => takeAction({ type: 'check_metrics', target: selectedService, params: {} })} disabled={!selectedService} />
                <ActionButton label="Check Config" onClick={() => takeAction({ type: 'check_config', target: selectedService, params: {} })} disabled={!selectedService} />
                <ActionButton label="Edit Config" onClick={() => takeAction({ type: 'edit_config', target: selectedService, params: {} })} disabled={!selectedService} variant="warning" />
                <ActionButton label="Rollback" onClick={() => takeAction({ type: 'rollback_deployment', target: selectedService, params: {} })} disabled={!selectedService} variant="warning" />
                <ActionButton label="Restart" onClick={() => takeAction({ type: 'restart_service', target: selectedService, params: {} })} disabled={!selectedService} variant="danger" />
                <ActionButton label="Reply Customer" onClick={() => takeAction({ type: 'reply_customer', target: null, params: {} })} />
                <ActionButton label="Resolve" onClick={() => takeAction({ type: 'mark_resolved', target: null, params: {} })} variant="success" />
              </div>
            </div>
          </div>

          {/* Alerts & Tickets */}
          <div className="space-y-4">
            <h3 className="text-[10px] font-bold text-gray-500 uppercase tracking-widest px-1">Active Incidents</h3>
            <div className="space-y-2">
              {obs.active_alerts.map(alert => (
                <div key={alert.id} className="bg-red-500/5 border border-red-500/20 p-3 rounded-lg flex gap-3">
                  <AlertCircle className="w-5 h-5 text-red-500 shrink-0" />
                  <div>
                    <p className="text-xs font-bold text-white">{alert.service.toUpperCase()}: {alert.message}</p>
                    <p className="text-[10px] text-red-500/70 mt-1 uppercase">{alert.severity} priority</p>
                  </div>
                </div>
              ))}
              {obs.customer_tickets.filter(t => t.status === 'open').map(ticket => (
                <div key={ticket.id} className="bg-orange-500/5 border border-orange-500/20 p-3 rounded-lg flex gap-3">
                  <MessageSquare className="w-5 h-5 text-orange-500 shrink-0" />
                  <div>
                    <p className="text-xs font-bold text-white">{ticket.customer}: "{ticket.message}"</p>
                    <p className="text-[10px] text-orange-500/70 mt-1 uppercase">Customer Ticket • Urgency {ticket.urgency}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

function StatCard({ label, value, color }: { label: string, value: string | number, color: string }) {
  return (
    <div className="bg-zinc-900/50 border border-white/10 p-4 rounded-xl">
      <p className="text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-1">{label}</p>
      <p className={`text-2xl font-black ${color}`}>{value}</p>
    </div>
  );
}

const ServiceCard: React.FC<{ service: ServiceState, isSelected: boolean, onClick: () => void }> = ({ service, isSelected, onClick }) => {
  const Icon = service.name.includes('db') || service.name.includes('database') ? Database : 
               service.name.includes('web') ? Globe : Server;
  
  const statusColor = service.status === 'running' ? 'text-green-500' : 
                      service.status === 'degraded' ? 'text-yellow-500' : 'text-red-500';

  return (
    <motion.div 
      whileHover={{ scale: 1.02 }}
      onClick={onClick}
      className={`cursor-pointer p-4 rounded-xl border transition-all ${
        isSelected ? 'bg-blue-500/10 border-blue-500' : 'bg-zinc-900/50 border-white/10 hover:border-white/20'
      }`}
    >
      <div className="flex items-center justify-between mb-4">
        <div className={`p-2 rounded-lg ${isSelected ? 'bg-blue-500/20' : 'bg-white/5'}`}>
          <Icon className={`w-5 h-5 ${isSelected ? 'text-blue-400' : 'text-gray-400'}`} />
        </div>
        <div className={`text-[10px] font-bold uppercase ${statusColor}`}>
          {service.status}
        </div>
      </div>
      <h4 className="text-sm font-bold text-white mb-3 tracking-tight">{service.name.toUpperCase()}</h4>
      
      <div className="space-y-2">
        <MetricBar label="Health" value={service.health * 100} color="bg-blue-500" />
        <MetricBar label="CPU" value={service.cpu} color="bg-red-500" />
        <MetricBar label="Mem" value={service.memory} color="bg-green-500" />
      </div>
    </motion.div>
  );
}

function MetricBar({ label, value, color }: { label: string, value: number, color: string }) {
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-[9px] font-bold uppercase text-gray-500">
        <span>{label}</span>
        <span>{Math.round(value)}%</span>
      </div>
      <div className="h-1 bg-white/5 rounded-full overflow-hidden">
        <motion.div 
          initial={{ width: 0 }}
          animate={{ width: `${value}%` }}
          className={`h-full ${color}`}
        />
      </div>
    </div>
  );
}

function ActionButton({ label, onClick, disabled, variant = 'default' }: { label: string, onClick: () => void, disabled?: boolean, variant?: 'default' | 'danger' | 'success' | 'warning' }) {
  const colors = {
    default: 'bg-zinc-800 hover:bg-zinc-700 text-gray-300',
    danger: 'bg-red-900/30 hover:bg-red-900/50 text-red-400 border border-red-500/20',
    success: 'bg-green-900/30 hover:bg-green-900/50 text-green-400 border border-green-500/20',
    warning: 'bg-yellow-900/30 hover:bg-yellow-900/50 text-yellow-400 border border-yellow-500/20'
  };

  return (
    <button 
      onClick={onClick}
      disabled={disabled}
      className={`px-3 py-2 rounded-md text-[10px] font-bold uppercase tracking-wider transition-all disabled:opacity-30 disabled:cursor-not-allowed ${colors[variant]}`}
    >
      {label}
    </button>
  );
}

function generateChartData(services: Record<string, ServiceState>) {
  return Object.values(services).map(s => ({
    name: s.name.substring(0, 4),
    health: s.health * 100,
    cpu: s.cpu,
    memory: s.memory
  }));
}
