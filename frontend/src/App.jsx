import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Shield, ShieldAlert, ShieldCheck, Wifi, Server, Smartphone, Activity, AlertTriangle, ArrowRight } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const API_URL = 'http://localhost:8000';

function App() {
  const [data, setData] = useState(null);
  const [history, setHistory] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchScanData = async () => {
    try {
      const [{ data: scanRes }, { data: histRes }] = await Promise.all([
        axios.get(`${API_URL}/scan`),
        axios.get(`${API_URL}/history`)
      ]);
      
      if (!scanRes.status) {
        setData(scanRes);
        setHistory(histRes);
      }
      setError(null);
      setLoading(false);
    } catch (err) {
      console.error(err);
      setError("Failed to connect to backend. Is FastAPI running?");
      setLoading(false);
    }
  };

  useEffect(() => {
    // Initial fetch
    fetchScanData();
    // Real-Time Polling Strategy EVERY 5 SECONDS as specified
    const interval = setInterval(() => fetchScanData(), 5000);
    return () => clearInterval(interval);
  }, []);

  const setDemoMode = async (mode) => {
    await axios.post(`${API_URL}/demo`, { mode });
    setTimeout(fetchScanData, 1000);
  };

  if (loading) return (
    <div className="flex bg-slate-950 items-center justify-center min-h-screen text-emerald-400 font-mono text-xl animate-pulse">
      <div>Initializing AI-Assisted Security Scanners...</div>
    </div>
  );

  if (error || !data) return (
    <div className="flex bg-slate-950 items-center justify-center min-h-screen text-red-500 font-mono text-xl">
      <div className="text-center">
        <AlertTriangle className="w-16 h-16 mx-auto mb-4" />
        <p>{error || "Awaiting Scanner Data..."}</p>
        <button onClick={fetchScanData} className="mt-8 px-6 py-2 bg-slate-800 rounded-lg hover:bg-slate-700 text-white transition">Retry Connection</button>
      </div>
    </div>
  );

  const risk = data.risk;
  const wifi = data.wifi;
  const net = data.network;

  const isHighRisk = risk.level === "HIGH" || risk.level === "CRITICAL";
  const isMedRisk = risk.level === "MEDIUM";

  return (
    <div className="min-h-screen p-6 md:p-10 select-none">
      
      {/* Header */}
      <header className="flex flex-col md:flex-row justify-between items-center mb-10 pb-6 border-b border-slate-800">
        <div className="flex items-center space-x-4 mb-4 md:mb-0">
          <div className={`p-3 rounded-xl shadow-lg border ${isHighRisk ? 'bg-red-500/20 border-red-500/50 text-red-400' : isMedRisk ? 'bg-amber-500/20 border-amber-500/50 text-amber-400' : 'bg-emerald-500/20 border-emerald-500/50 text-emerald-400'}`}>
            {isHighRisk ? <ShieldAlert size={32} /> : isMedRisk ? <Shield size={32} /> : <ShieldCheck size={32} />}
          </div>
          <div>
            <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-emerald-400 tracking-tight">AI Wi-Fi Security Dashboard</h1>
            <p className="text-slate-400 text-sm mt-1 flex items-center">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse mr-2"></span>
              Live Monitoring • Last Update: {new Date(data.timestamp).toLocaleTimeString()}
            </p>
          </div>
        </div>

        {/* Demo Toggles for Viva */}
        <div className="flex space-x-3 bg-slate-900/80 p-2 rounded-xl border border-slate-800">
          <button onClick={() => setDemoMode("real")} className={`px-4 py-2 rounded-lg text-sm font-medium transition ${!data.scenario ? 'bg-blue-600' : 'hover:bg-slate-800'}`}>Real Data</button>
          <button onClick={() => setDemoMode("scenario_1")} className={`px-4 py-2 rounded-lg text-sm font-medium transition text-red-300 ${data.scenario === "scenario_1" ? 'bg-red-900/50 border border-red-500/50' : 'hover:bg-slate-800'}`}>Weak Wi-Fi</button>
          <button onClick={() => setDemoMode("scenario_2")} className={`px-4 py-2 rounded-lg text-sm font-medium transition text-emerald-300 ${data.scenario === "scenario_2" ? 'bg-emerald-900/50 border border-emerald-500/50' : 'hover:bg-slate-800'}`}>Secure Wi-Fi</button>
        </div>
      </header>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        
        {/* Risk Score Panel (Large) */}
        <div className="glass-panel col-span-1 lg:col-span-1 flex flex-col items-center justify-center p-8 relative overflow-hidden group">
          <div className={`absolute inset-0 opacity-10 blur-3xl transition-colors duration-1000 ${isHighRisk ? 'bg-red-600' : isMedRisk ? 'bg-amber-600' : 'bg-emerald-600'}`}></div>
          <h2 className="text-slate-400 font-semibold uppercase tracking-wider text-sm mb-6 z-10">AI Risk Score</h2>
          
          <div className="relative z-10">
            {/* Animated Gauge placeholder */}
            <svg viewBox="0 0 36 36" className={`w-48 h-48 transform -rotate-90 ${isHighRisk ? 'text-red-500' : isMedRisk ? 'text-amber-500' : 'text-emerald-500'}`}>
              <path className="text-slate-800" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="currentColor" strokeWidth="2" strokeDasharray="100, 100" />
              <path className="transition-all duration-1000 ease-out drop-shadow-lg" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="currentColor" strokeWidth="3" strokeDasharray={`${risk.score}, 100`} />
            </svg>
            <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-center">
              <span className="text-5xl font-black">{risk.score}</span>
              <span className="block text-xs font-bold uppercase tracking-widest mt-1 opacity-80">{risk.level}</span>
            </div>
          </div>
          <div className="mt-8 text-center z-10 w-full">
            <div className="flex justify-between text-xs text-slate-500 px-4">
              <span>ML Score: {risk.components?.ml_score}</span>
              <span>Rule Score: {risk.components?.rule_score}</span>
            </div>
            <div className="w-full h-1.5 bg-slate-800 rounded-full mt-2 overflow-hidden">
              <div className="h-full bg-blue-500/50" style={{ width: `60%` }}></div>
            </div>
          </div>
        </div>

        <div className="col-span-1 lg:col-span-3 grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Wi-Fi Info Panel */}
          <div className="glass-panel p-6 relative overflow-hidden group hover:border-blue-500/30 transition-colors">
            <div className="absolute right-0 top-0 opacity-5 drop-shadow-2xl group-hover:scale-110 transition-transform"><Wifi size={160}/></div>
            <h2 className="text-blue-400 font-semibold uppercase tracking-wider text-sm mb-4 flex items-center"><Wifi size={16} className="mr-2"/> Interface Layer</h2>
            <div className="space-y-4">
              <div>
                <p className="text-slate-500 text-xs">SSID</p>
                <p className="font-bold text-xl truncate">{wifi.ssid || 'Unknown'}</p>
              </div>
              <div className="flex justify-between">
                <div>
                  <p className="text-slate-500 text-xs">Auth</p>
                  <p className={`font-semibold ${wifi.authentication?.includes('Open') ? 'text-red-400' : 'text-slate-200'}`}>{wifi.authentication}</p>
                </div>
                <div>
                  <p className="text-slate-500 text-xs">Signal</p>
                  <p className="font-semibold text-slate-200">{wifi.signal_strength}%</p>
                </div>
              </div>
            </div>
          </div>

          {/* Security Panel */}
          <div className="glass-panel p-6 relative overflow-hidden group hover:border-red-500/30 transition-colors">
            <div className="absolute right-0 top-0 opacity-5 drop-shadow-2xl group-hover:scale-110 transition-transform"><Server size={160}/></div>
            <h2 className="text-red-400 font-semibold uppercase tracking-wider text-sm mb-4 flex items-center"><Server size={16} className="mr-2"/> Infrastructure Layer</h2>
            <div className="space-y-4">
              <div>
                <p className="text-slate-500 text-xs">Gateway IP</p>
                <p className="font-mono text-lg">{net.gateway_ip}</p>
              </div>
              <div>
                <div className="flex justify-between items-baseline">
                  <p className="text-slate-500 text-xs">Open Ports</p>
                  <span className={`text-xs px-2 py-0.5 rounded-full ${net.port_scan_results?.open_ports > 0 ? 'bg-red-500/20 text-red-400' : 'bg-emerald-500/20 text-emerald-400'}`}>
                    {net.port_scan_results?.open_ports} detected
                  </span>
                </div>
                {net.port_scan_results?.risky_ports?.length > 0 ? (
                  <p className="font-bold text-red-500 text-sm mt-1 truncate">{net.port_scan_results.risky_ports.join(', ')}</p>
                ) : (
                  <p className="font-semibold text-emerald-500/80 text-sm mt-1">No severe misconfigs</p>
                )}
              </div>
            </div>
          </div>

          {/* Devices Summary Panel */}
          <div className="glass-panel p-6 relative overflow-hidden group hover:border-amber-500/30 transition-colors">
            <div className="absolute right-0 top-0 opacity-5 drop-shadow-2xl group-hover:scale-110 transition-transform"><Smartphone size={160}/></div>
            <h2 className="text-amber-400 font-semibold uppercase tracking-wider text-sm mb-4 flex items-center"><Smartphone size={16} className="mr-2"/> Device Layer</h2>
            <div className="space-y-4">
              <div className="flex justify-between items-end">
                <div>
                  <p className="text-slate-500 text-xs">Active Connects</p>
                  <p className="font-bold text-4xl">{net.device_count}</p>
                </div>
                <div className="text-right">
                  <p className="text-slate-500 text-xs">Unknown</p>
                  <p className={`font-bold text-2xl ${net.unknown_devices > 0 ? 'text-amber-500' : 'text-emerald-500'}`}>{net.unknown_devices}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

      </div>

      {/* Bottom Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
        
        {/* Device List Table */}
        <div className="glass-panel p-6 max-h-80 flex flex-col">
          <h2 className="text-slate-200 font-semibold mb-4">Network Devices map</h2>
          <div className="overflow-y-auto flex-1 pr-2 space-y-2 custom-scrollbar">
            {net.devices?.map((dev, idx) => (
              <div key={idx} className={`flex items-center justify-between p-3 rounded-xl border ${dev.is_unknown ? 'bg-red-500/5 border-red-500/20 hover:border-red-500/40' : 'bg-slate-800/20 border-slate-700/50 hover:border-blue-500/30'} transition-colors`}>
                <div className="flex items-center space-x-3">
                  <Smartphone className={dev.is_unknown ? "text-red-400" : "text-blue-400"} size={20} />
                  <div>
                    <p className="font-mono text-sm text-slate-300">{dev.ip}</p>
                    <p className="text-xs text-slate-500 font-mono">{dev.mac}</p>
                  </div>
                </div>
                <span className={`text-xs px-2.5 py-1 rounded-full font-medium ${dev.is_unknown ? 'bg-red-500/20 text-red-400' : 'bg-slate-700 text-slate-400'}`}>
                  {dev.vendor}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* AI Recommendations & Graph */}
        <div className="flex flex-col gap-6">
          <div className="glass-panel p-6 flex-1">
            <h2 className="text-slate-200 font-semibold mb-4 flex items-center"><Activity size={18} className="mr-2 text-blue-400"/> AI Recommendations</h2>
            <ul className="space-y-3">
              {risk.recommendations?.map((rec, idx) => {
                const isCritical = rec.includes("CRITICAL") || rec.includes("immediately");
                const isUpgrade = rec.includes("Upgrade");
                return (
                  <li key={idx} className={`flex p-3 rounded-xl border ${isCritical ? 'bg-red-500/10 border-red-500/30 text-red-200' : isUpgrade ? 'bg-blue-500/10 border-blue-500/30 text-blue-200' : 'bg-amber-500/10 border-amber-500/30 text-amber-200'} text-sm`}>
                    <ArrowRight size={16} className={`mr-3 mt-0.5 shrink-0 ${isCritical ? 'text-red-400' : isUpgrade ? 'text-blue-400' : 'text-amber-400'}`}/>
                    <span>{rec}</span>
                  </li>
                );
              })}
            </ul>
          </div>

          <div className="glass-panel p-6 flex-1 h-36">
            <h2 className="text-slate-500 text-xs uppercase tracking-wider mb-2 font-bold">Historical Risk Trend</h2>
            <div className="w-full h-24">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={history}>
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', borderRadius: '8px' }}
                    itemStyle={{ color: '#ec4899' }}
                  />
                  <Line type="monotone" dataKey="risk_score" stroke="#10b981" strokeWidth={3} dot={false} animationDuration={500}/>
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

      </div>

    </div>
  );
}

export default App;
