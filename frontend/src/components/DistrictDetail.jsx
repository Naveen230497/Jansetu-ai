import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { AlertCircle, Activity, Building, Users } from 'lucide-react';
import { getPriorities, getRequests } from '../services/api';

export default function DistrictDetail() {
  const [priorities, setPriorities] = useState([]);
  const [allRequests, setAllRequests] = useState([]);
  const [selectedDistrict, setSelectedDistrict] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const [prioData, reqData] = await Promise.all([
          getPriorities(),
          getRequests()
        ]);
        setPriorities(prioData || []);
        setAllRequests(reqData || []);
        if (prioData && prioData.length > 0) {
          setSelectedDistrict(prioData[0].district_name);
        }
      } catch (err) {
        console.error('Failed to load district data:', err);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-xl font-medium text-slate-500 animate-pulse tracking-widest uppercase">Syncing Neural Sectors...</div>
      </div>
    );
  }

  const districtNames = [...new Set(priorities.map(p => p.district_name))];
  const currentPriority = priorities.find(p => p.district_name === selectedDistrict) || priorities[0] || null;
  const districtRequests = allRequests.filter(r => r.location_district === (currentPriority?.district_name || selectedDistrict));

  // Category breakdown for chart
  const categoryBreakdown = currentPriority?.category_breakdown || {};
  const categoryData = Object.entries(categoryBreakdown).map(([name, count]) => ({
    name, count
  })).sort((a, b) => b.count - a.count);

  const score = currentPriority ? Math.round(currentPriority.priority_score) : 0;

  if (priorities.length === 0 || !currentPriority) {
    return (
      <div className="flex flex-col items-center justify-center h-full premium-glass p-10 text-center relative overflow-hidden">
        <h3 className="text-xl font-black text-white mb-2 tracking-widest uppercase">No District Data</h3>
        <p className="text-slate-400">Ensure the backend is running and data exists in the system.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6 pb-10">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center premium-glass p-6 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-500/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2 pointer-events-none"></div>
        <div className="relative z-10">
          <h2 className="text-2xl font-black text-white uppercase tracking-widest">Sector Deep-Dive</h2>
          <p className="text-xs font-mono text-slate-400 mt-1 uppercase tracking-widest">Priority analysis with scoring breakdown</p>
        </div>
        <div className="mt-4 sm:mt-0 w-full sm:w-auto relative z-10">
          <select
            className="bg-black/60 border border-white/[0.1] text-slate-300 text-xs font-bold tracking-widest uppercase rounded-xl focus:ring-indigo-500 focus:border-indigo-500 block p-3 appearance-none transition-all hover:border-white/[0.2]"
            value={selectedDistrict}
            onChange={(e) => setSelectedDistrict(e.target.value)}
          >
            {districtNames.map(d => <option key={d} value={d}>{d}</option>)}
          </select>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Priority Score Card */}
        <div className="premium-glass p-6 flex flex-col items-center justify-center relative overflow-hidden text-center h-full">
          <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/5 to-transparent pointer-events-none"></div>
          <h3 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-6">Aggregate Threat Score</h3>
          <div className="relative">
            <svg className="w-32 h-32 transform -rotate-90">
              <circle cx="64" cy="64" r="56" fill="transparent" stroke="rgba(255,255,255,0.05)" strokeWidth="12" />
              <circle 
                cx="64" cy="64" r="56" fill="transparent" 
                stroke={score > 70 ? '#ef4444' : score > 40 ? '#f59e0b' : '#10b981'} 
                strokeWidth="12" 
                strokeDasharray="351.85" 
                strokeDashoffset={351.85 - (351.85 * score) / 100}
                className="transition-all duration-1000 ease-out"
                strokeLinecap="round"
              />
            </svg>
            <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
              <span className="text-4xl font-black text-white">{score}</span>
            </div>
          </div>
          <p className={`mt-6 text-sm font-bold uppercase tracking-widest ${score > 70 ? 'text-red-400' : score > 40 ? 'text-amber-400' : 'text-emerald-400'}`}>
            {score > 70 ? 'Critical Priority' : score > 40 ? 'Elevated Priority' : 'Standard Priority'}
          </p>
        </div>

        {/* Stats Grid */}
        <div className="lg:col-span-2 grid grid-cols-2 gap-4">
          <div className="premium-glass p-6">
            <div className="flex items-center mb-2">
              <AlertCircle className="h-5 w-5 text-indigo-400 mr-2" />
              <h3 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Total Reports</h3>
            </div>
            <p className="text-4xl font-black text-white">{currentPriority.total_requests || 0}</p>
          </div>
          
          <div className="premium-glass p-6">
            <div className="flex items-center mb-2">
              <Activity className="h-5 w-5 text-emerald-400 mr-2" />
              <h3 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Urgency Average</h3>
            </div>
            <p className="text-4xl font-black text-white">{((currentPriority.urgency_factor || 0) * 5).toFixed(1)} <span className="text-lg text-slate-500 font-normal">/ 5.0</span></p>
          </div>
          
          <div className="premium-glass p-6">
            <div className="flex items-center mb-2">
              <Building className="h-5 w-5 text-amber-400 mr-2" />
              <h3 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Infra Gap Index</h3>
            </div>
            <p className="text-4xl font-black text-white">{(currentPriority.infra_gap * 100).toFixed(0)}%</p>
          </div>
          
          <div className="premium-glass p-6">
            <div className="flex items-center mb-2">
              <Users className="h-5 w-5 text-purple-400 mr-2" />
              <h3 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Sentiments</h3>
            </div>
            <div className="flex space-x-2 mt-2">
              <span className="text-xs bg-red-500/20 text-red-400 border border-red-500/30 px-2 py-1 rounded font-mono">NEG</span>
              <span className="text-xs bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 px-2 py-1 rounded font-mono">POS</span>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="premium-glass p-6 h-[350px]">
          <h3 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-6">Threat Vectors by Volume</h3>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={categoryData} layout="vertical" margin={{ top: 0, right: 30, left: 20, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" horizontal={false} />
              <XAxis type="number" stroke="#94a3b8" tick={{fill: '#94a3b8', fontSize: 10}} />
              <YAxis dataKey="name" type="category" stroke="#94a3b8" tick={{fill: '#94a3b8', fontSize: 10}} width={80} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px' }}
                itemStyle={{ color: '#e2e8f0' }}
              />
              <Bar dataKey="count" fill="#4f46e5" radius={[0, 4, 4, 0]} barSize={20} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="premium-glass p-6 flex flex-col h-[350px]">
          <h3 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-4">Raw Intercept Data</h3>
          <div className="overflow-y-auto flex-1 pr-2 space-y-3">
            {districtRequests.length > 0 ? districtRequests.map((req, i) => (
              <div key={i} className="p-3 bg-black/40 border border-white/[0.05] rounded-lg">
                <div className="flex justify-between items-start mb-1">
                  <span className="text-[10px] font-bold text-indigo-400 uppercase tracking-widest">{req.category}</span>
                  <span className={`text-[9px] font-bold uppercase tracking-widest px-2 py-0.5 rounded ${
                    req.urgency >= 4 ? 'bg-red-500/20 text-red-400' :
                    req.urgency >= 3 ? 'bg-amber-500/20 text-amber-400' : 'bg-emerald-500/20 text-emerald-400'
                  }`}>
                    Urgency {req.urgency}
                  </span>
                </div>
                <p className="text-xs text-slate-300 leading-relaxed mb-2">{req.translated_text || req.raw_text}</p>
                <div className="flex justify-between items-center mt-2 border-t border-white/[0.05] pt-2">
                  <span className="text-[9px] text-slate-500">{new Date(req.timestamp).toLocaleDateString()}</span>
                  <span className="text-[9px] text-slate-500 uppercase tracking-widest">{req.language_detected}</span>
                </div>
              </div>
            )) : (
              <div className="text-center text-slate-500 py-10 text-sm font-mono">No raw data available</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
