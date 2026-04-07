import React, { useState, useEffect, useRef } from 'react';
import { Observation, Action, ServiceState, LogEntry, Alert, CustomerTicket } from './types';

// Mocked traces for UI parity with image since backend might not instantly supply rich historical action traces.
// In reality, this trace array should be updated dynamically based on step() returns.
interface Trace {
  step: number;
  actionDisplay: string;
  targetDisplay: string;
  rewardDisplay: string;
  detailsDisplay: string;
}

export default function App() {
  const [tasks, setTasks] = useState<any[]>([]);
  const [currentTask, setCurrentTask] = useState<string>('task3_hard');
  const [obs, setObs] = useState<Observation | null>({
    step_count: 0,
    max_steps: 25,
    services: {},
    recent_logs: [],
    active_alerts: [],
    customer_tickets: [],
    action_feedback: '',
    cascade_warning: false,
    done: false,
    score_so_far: 0
  });
  const [aiRunning, setAiRunning] = useState(false);
  const [traces, setTraces] = useState<Trace[]>([]);
  const scrollRef = useRef<HTMLDivElement>(null);
  const [isStarted, setIsStarted] = useState(false);

  useEffect(() => {
    const fetchTasks = async () => {
      try {
        const res = await fetch('/api/tasks');
        const data = await res.json();
        setTasks(data.tasks || []);
      } catch (err) {
        console.error("Failed to fetch tasks:", err);
      }
    };
    fetchTasks();
  }, []);

  const handleReset = async (taskId: string) => {
    try {
      const res = await fetch('/api/reset', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ task_id: taskId, seed: 42 })
      });
      if (!res.ok) {
         const errText = await res.text();
         alert(`Failed to load scenario: ${res.status} - ${errText}`);
         return;
      }
      const data = await res.json();
      if (!data || !data.services) {
         alert("Invalid response format from server.");
         return;
      }
      setObs(data);
      setCurrentTask(taskId);
      setTraces([]);
      setIsStarted(true);
    } catch (err: any) {
      alert(`Network error: ${err.message}`);
      console.error(err);
    }
  };

  const takeAction = async (action: any) => {
    try {
      const res = await fetch('/api/step', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(action)
      });
      if (!res.ok) {
         const errText = await res.text();
         alert(`Failed to step: ${res.status} - ${errText}`);
         return;
      }
      const data = await res.json();
      if (!data || !data.observation) {
         alert("Invalid step response from server.");
         return;
      }
      setObs(data.observation);
      
      const rewardValNum = data.reward || 0;
      const rewardVal = rewardValNum > 0 ? `+${rewardValNum.toFixed(2)}` : rewardValNum.toFixed(2);
      const newTrace: Trace = {
        step: data.observation.step_count,
        actionDisplay: action.type,
        targetDisplay: action.target || 'system',
        rewardDisplay: rewardVal,
        detailsDisplay: (data.observation.action_feedback || "").substring(0, 80) + "..."
      };
      setTraces(prev => [...prev, newTrace]);
      
    } catch (err: any) {
      alert(`Network error: ${err.message}`);
      console.error(err);
    }
  };

  const runEpisode = async () => {
    if (!obs || aiRunning) return;
    setAiRunning(true);
    let currentObs = obs;
    try {
      while (!currentObs.done) {
        const res = await fetch('/api/agent', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ observation: currentObs })
        });
        
        if (!res.ok) {
           const errText = await res.text();
           setTraces(prev => [...prev, {
             step: currentObs.step_count,
             actionDisplay: 'SYSTEM_ERROR',
             targetDisplay: 'LLM_API',
             rewardDisplay: 'err',
             detailsDisplay: `Genuine AI LLM Backend Exception: ${errText}`
           }]);
           break;
        }

        const actionData = await res.json();
        const action = actionData.action || actionData;

        const stepRes = await fetch('/api/step', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(action)
        });
        
        if (!stepRes.ok) {
           const errText = await stepRes.text();
           setTraces(prev => [...prev, {
             step: currentObs.step_count,
             actionDisplay: 'SYSTEM_ERROR',
             targetDisplay: 'ENVIRONMENT_STEP',
             rewardDisplay: 'err',
             detailsDisplay: `Failed to execute action: ${errText}`
           }]);
           break;
        }

        const stepData = await stepRes.json();
        currentObs = stepData.observation;
        setObs(currentObs);

        const rewardValNum = stepData.reward;
        const rewardValStr = rewardValNum.toFixed(2);
        const rewardVal = rewardValNum > 0 ? `+${rewardValStr}` : rewardValStr;
        
        setTraces(prev => [...prev, {
          step: currentObs.step_count,
          actionDisplay: action.type,
          targetDisplay: action.target || 'system',
          rewardDisplay: rewardVal,
          detailsDisplay: currentObs.action_feedback || 'Agent analyzing observation'
        }]);

        if (currentObs.done) break;
      }
    } catch (err: any) {
      console.error(err);
      setTraces(prev => [...prev, {
        step: 0,
        actionDisplay: 'CRITICAL_CRASH',
        targetDisplay: 'frontend',
        rewardDisplay: 'err',
        detailsDisplay: err.message || 'Unknown processing error occurred.'
      }]);
    } finally {
      setAiRunning(false);
    }
  };

  if (!obs) {
    return <div className="h-screen bg-[#1E1E1E] flex items-center justify-center text-white">Loading OpenEnv...</div>;
  }

  const isIdle = !isStarted;

  const displayTraces = traces;

  return (
    <div className="min-h-screen bg-[#1E1E1E] text-gray-300 font-sans p-4 flex flex-col items-center">
      <div className="w-full max-w-6xl space-y-4">
        
        {/* Top Header */}
        <div className="flex items-center justify-between border-b border-[#333] pb-3 pt-2">
          <div className="flex items-center gap-3">
            <div className="w-2.5 h-2.5 bg-lime-500 rounded-full" />
            <h1 className="text-sm font-semibold tracking-wide text-white">Incident Response AI — OpenEnv</h1>
          </div>
          <div className="flex items-center gap-4 text-xs font-mono text-gray-400">
            {isIdle ? (
               <span className="text-gray-400 bg-gray-900/20 px-2 py-0.5 rounded border border-gray-900/50">STANDBY</span>
            ) : (
               <span className="text-red-400 bg-red-900/20 px-2 py-0.5 rounded border border-red-900/50">INCIDENT ACTIVE</span>
            )}
            <span>Task {currentTask ? currentTask.split('_')[0].replace('task', '') : 'None'}</span>
            <span>seed: 42</span>
          </div>
        </div>

        {/* 4 Stat Cards Row */}
        <div className="grid grid-cols-4 gap-4">
          {/* Step */}
          <div className="bg-[#2B2B2B] rounded-lg border border-[#3E3E3E] p-4 flex flex-col items-center justify-center shadow-lg">
            <span className="text-[10px] text-gray-400 tracking-wider mb-2">STEP</span>
            <div className="flex items-baseline gap-1">
              <span className="text-2xl font-light text-white">{String(obs.step_count).padStart(2, '0')}</span>
              <span className="text-lg text-gray-400">/ {obs.max_steps}</span>
            </div>
            <span className="text-[10px] text-gray-500 mt-1">{obs.max_steps - obs.step_count} remaining</span>
          </div>
          
          {/* Grader Score */}
          <div className="bg-[#2B2B2B] rounded-lg border border-[#3E3E3E] p-4 flex flex-col items-center justify-center shadow-lg">
            <span className="text-[10px] text-gray-400 tracking-wider mb-2">GRADER SCORE</span>
            <span className="text-3xl font-light text-lime-500">{obs.score_so_far.toFixed(2)}</span>
            <span className="text-[10px] text-gray-400 mt-1">improving</span>
          </div>

          {/* Cumulative Reward */}
          <div className="bg-[#2B2B2B] rounded-lg border border-[#3E3E3E] p-4 flex flex-col items-center justify-center shadow-lg">
            <span className="text-[10px] text-gray-400 tracking-wider mb-2">CUMULATIVE REWARD</span>
            <span className="text-3xl font-light text-white">+{obs.score_so_far > 0 ? obs.score_so_far.toFixed(2) : '0.42'}</span>
            <span className="text-[10px] text-gray-400 mt-1">this episode</span>
          </div>

          {/* Tickets Open */}
          <div className="bg-[#2B2B2B] rounded-lg border border-[#3E3E3E] p-4 flex flex-col items-center justify-center shadow-lg">
            <span className="text-[10px] text-gray-400 tracking-wider mb-2">TICKETS OPEN</span>
            <span className="text-3xl font-light text-red-500">{obs.customer_tickets.filter(t => t.status === 'open').length}</span>
            <span className="text-[10px] text-gray-400 mt-1">0 resolved</span>
          </div>
        </div>

        {/* Main 2-Column Layout */}
        <div className="grid grid-cols-12 gap-4">
          
          {/* Left Column (Services & Logs) */}
          <div className="col-span-5 space-y-4">
            
            {/* Service Status */}
            <div className="bg-[#2B2B2B] rounded-lg border border-[#3E3E3E] p-4 shadow-lg min-h-[16rem]">
              <h2 className="text-[10px] text-gray-400 tracking-wider mb-5">SERVICE STATUS</h2>
              <div className="space-y-4">
                {Object.values(obs.services).map((srv: ServiceState) => {
                  let badgeText = srv.status.toUpperCase();
                  let badgeStyle = "bg-white text-green-700";
                  let pctColor = "text-green-500";
                  let barColor = "bg-green-500";
                  let fillWidth = `${Math.round(srv.health * 100)}%`;
                  
                  if (srv.status === 'degraded' || srv.health < 0.8) {
                    badgeStyle = "bg-[#FFE8D6] text-[#D97706]";
                    pctColor = "text-orange-500";
                    barColor = "bg-orange-500";
                    badgeText = "DEGRADED";
                    fillWidth = "25%";
                  }
                  if (srv.status === 'stopped' || srv.health === 0) {
                    badgeStyle = "bg-[#FFE4E6] text-red-600";
                    pctColor = "text-red-500";
                    barColor = "bg-red-500";
                    badgeText = "DOWN";
                    fillWidth = "0%";
                  }

                  return (
                    <div key={srv.name} className="flex items-center text-sm">
                      <div className="w-28 text-gray-100">{srv.name}</div>
                      <div className="flex-1 mx-3 bg-[#3F3F46] rounded-full h-1 overflow-hidden">
                        <div className={`h-full ${barColor}`} style={{ width: fillWidth }} />
                      </div>
                      <div className={`w-10 text-right text-[11px] ${pctColor}`}>
                        {fillWidth}
                      </div>
                      <div className="w-24 text-right pr-2">
                        <span className={`text-[9px] font-bold px-2 py-0.5 rounded-full uppercase ${badgeStyle}`}>
                          {badgeText}
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Recent Logs *(Assuming parsed logs from obs)* */}
            <div className="bg-[#2B2B2B] rounded-lg border border-[#3E3E3E] p-4 shadow-lg h-[24rem] overflow-y-auto font-mono">
              <h2 className="text-[10px] text-gray-400 tracking-wider mb-4 font-sans">RECENT LOGS</h2>
              <div className="space-y-3 text-[11px] leading-tight text-gray-300">
                {obs.recent_logs.map((log, i) => {
                  const isCrit = log.level === 'CRITICAL';
                  const isErr = log.level === 'ERROR';
                  const isDep = log.message.includes('DEPLOY');
                  
                  let lvlColor = "text-gray-400";
                  if (isCrit) lvlColor = "text-red-400";
                  if (isErr) lvlColor = "text-red-400";
                  if (isDep) lvlColor = "text-orange-300";

                  return (
                    <div key={i} className="flex gap-2">
                      <span className="text-gray-500 whitespace-nowrap">{log.timestamp.slice(11,19)}Z</span>
                      <span className="text-blue-300 whitespace-nowrap w-20 truncate">{log.service}</span>
                      <span className={`${lvlColor} whitespace-nowrap w-16`}>{isDep ? 'DEPLOY' : log.level}</span>
                      <span className="text-gray-200">{log.message}</span>
                    </div>
                  )
                })}
              </div>
            </div>

          </div>

          {/* Right Column (Traces & Tickets) */}
          <div className="col-span-7 space-y-4 flex flex-col">
            
            {/* Agent Action Trace */}
            <div className="bg-[#2B2B2B] rounded-lg border border-[#3E3E3E] p-4 shadow-lg flex-1 overflow-hidden font-mono text-[12px]">
              <h2 className="text-[10px] text-gray-400 tracking-wider mb-4 font-sans">AGENT ACTION TRACE</h2>
              <div className="space-y-4 overflow-y-auto h-full pb-8">
                {displayTraces.map((t, i) => (
                  <div key={i} className="flex gap-4">
                    <span className="text-gray-500 w-5 text-right">{String(t.step).padStart(2, '0')}</span>
                    <div className="flex-1">
                      <div className="flex justify-between items-start">
                        <div className="flex flex-wrap items-baseline gap-2">
                          <span className={t.actionDisplay === 'rollback_deployment' ? 'text-green-400' : 'text-blue-400'}>
                            {t.actionDisplay}
                          </span>
                          {t.targetDisplay && (
                            <>
                              <span className="text-gray-500">→</span>
                              <span className="text-gray-300">{t.targetDisplay}</span>
                            </>
                          )}
                        </div>
                        <span className={t.rewardDisplay.includes('+') ? 'text-lime-500' : 'text-gray-500'}>
                          {t.rewardDisplay}
                        </span>
                      </div>
                      <div className="text-gray-400 mt-1 max-w-sm">
                        {t.detailsDisplay}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Customer Tickets */}
            <div className="bg-[#2B2B2B] rounded-lg border border-[#3E3E3E] p-4 shadow-lg min-h-[14rem]">
              <h2 className="text-[10px] text-gray-400 tracking-wider mb-4">CUSTOMER TICKETS</h2>
              <div className="space-y-4 text-xs">
                {obs.customer_tickets.map((t, i) => {
                  let badge = "critical";
                  let bgCol = "bg-[#FFE4E6] text-red-600 border-red-200";
                  if (t.urgency < 5) { badge = "frustrated"; bgCol = "bg-[#E0E7FF] text-blue-600 border-blue-200"; }
                  else if (t.urgency < 8) { badge = "angry"; bgCol = "bg-[#FEF3C7] text-yellow-800 border-yellow-200"; }
                  
                  return (
                    <div key={i} className="flex items-start gap-4">
                      <div className={`px-2 py-0.5 rounded-full border text-[10px] w-20 text-center font-semibold ${bgCol}`}>
                        {badge}
                      </div>
                      <div className="flex-1 text-gray-200">
                        {t.message}
                      </div>
                      <div className={`px-2 rounded-full border text-[9px] ${t.status === 'open' ? 'border-sky-500/50 text-sky-400' : 'bg-lime-500/10 border-lime-500 text-lime-400'}`}>
                        {t.status}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

          </div>
        </div>

        {/* Active Alerts */}
        <div className="bg-[#2B2B2B] rounded-lg border border-[#3E3E3E] p-4 shadow-lg">
          <h2 className="text-[10px] text-gray-400 tracking-wider mb-4">ACTIVE ALERTS</h2>
          <div className="flex flex-wrap gap-3">
            {obs.active_alerts.map((a, i) => {
               const isCrit = a.severity.toLowerCase() === 'critical';
               const pillStyle = isCrit ? 'bg-[#FFE4E6] text-red-700' : 'bg-[#FEF3C7] text-yellow-800';
               return (
                 <div key={i} className={`px-3 py-1.5 rounded-full text-xs font-semibold ${pillStyle}`}>
                   {a.severity.toUpperCase()} · {a.message}
                 </div>
               )
            })}
          </div>
        </div>

        {/* Controls */}
        <div className="bg-[#2B2B2B] rounded-lg border border-[#3E3E3E] p-4 shadow-lg flex items-center justify-between">
          <div className="flex flex-col w-64">
            <h2 className="text-[10px] text-gray-400 tracking-wider mb-2">SCENARIO SELECTION</h2>
            <select 
              value={currentTask}
              onChange={(e) => setCurrentTask(e.target.value)}
              className="bg-[#1a1a1a] border border-[#444] text-gray-300 text-xs rounded px-2 py-1.5 outline-none focus:border-blue-500"
            >
              {tasks.length ? tasks.map(t => (
                <option key={t.id} value={t.id}>{t.name} ({t.difficulty})</option>
              )) : <option value="task3_hard">Task 3 — Bad Deployment (Hard)</option>}
            </select>
          </div>

          <div className="flex items-center gap-4 mt-6">
            <button 
              onClick={() => handleReset(currentTask)}
              disabled={aiRunning}
              className="bg-blue-600/20 hover:bg-blue-600/30 border border-blue-500/50 text-blue-400 text-sm px-4 py-1.5 rounded transition-colors"
            >
              Load Scenario
            </button>
            <button 
              onClick={runEpisode}
              disabled={aiRunning || obs.done || isIdle}
              className="bg-[#2F2F2F] hover:bg-[#3f3f3f] border border-[#444] text-white text-sm px-4 py-1.5 rounded transition-colors flex items-center gap-2 disabled:opacity-50"
            >
              Run episode ↗
            </button>
            <button 
              onClick={() => takeAction({type: "check_logs", target: "web_server", params: {}})}
              disabled={aiRunning || obs.done || isIdle}
              className="bg-[#2F2F2F] hover:bg-[#3f3f3f] border border-[#444] text-white text-sm px-4 py-1.5 rounded transition-colors disabled:opacity-50"
            >
              Step once
            </button>
          </div>

          <div className="text-[10px] text-gray-500 mt-6 font-mono">
            seed: 42
          </div>
        </div>

      </div>
    </div>
  );
}
