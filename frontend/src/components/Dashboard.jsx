import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { FileText, Languages, MapPin, AlertTriangle, Activity, Zap, ShieldAlert, Globe } from 'lucide-react';
import { APIProvider, Map, AdvancedMarker, Pin } from '@vis.gl/react-google-maps';
import { getStats, getPriorities, getRequests } from '../services/api';

const API_KEY = import.meta.env.VITE_GOOGLE_MAPS_API_KEY || '';
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const WS_BASE = API_BASE.replace(/^http/, 'ws') + '/ws/live';

const formatTime = (ts) => {
  if (!ts) return new Date().toLocaleTimeString();
  let str = String(ts);
  if (!str.endsWith('Z') && !str.includes('+')) {
    str += 'Z';
  }
  const date = new Date(str);
  return isNaN(date.getTime()) ? new Date().toLocaleTimeString() : date.toLocaleTimeString();
};

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4'];

export default function Dashboard() {
  const [loading, setLoading] = useState(true);
  const [simulatorRunning, setSimulatorRunning] = useState(false);
  const [mapMarkers, setMapMarkers] = useState([]);
  const [data, setData] = useState({
    stats: { totalRequests: 0, languages: 0, districts: 0, avgUrgency: 0 },
    categoryData: [],
    languageData: [],
    topDistricts: [],
    recentRequests: []
  });

  useEffect(() => {
    async function fetchData() {
      try {
        const [statsRes, prioRes, reqsRes] = await Promise.all([
          getStats(),
          getPriorities(),
          getRequests()
        ]);
        
        const catData = Object.entries(statsRes?.categories || {}).map(([name, count]) => ({ name, count }));
        const langData = Object.entries(statsRes?.languages || {}).map(([name, count]) => ({ name, count }));
        
        setData({
          stats: {
            totalRequests: statsRes?.total_requests || 0,
            languages: Object.keys(statsRes?.languages || {}).length,
            districts: prioRes?.length || 0,
            avgUrgency: statsRes?.avg_urgency?.toFixed(1) || 0
          },
          categoryData: catData,
          languageData: langData,
          topDistricts: prioRes?.slice(0, 5) || [],
          recentRequests: (reqsRes || []).slice(0, 8).map(r => ({
            id: r.id,
            text: r.translated_text || r.raw_text,
            category: r.category,
            urgency: r.urgency >= 4 ? 'High' : r.urgency >= 3 ? 'Medium' : 'Low',
            time: formatTime(r.timestamp),
            language: r.language_detected
          }))
        });

        // Set map markers with highlight for newest items
        const sortedReqs = [...(reqsRes || [])].sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
        const newestIds = new Set(sortedReqs.slice(0, 3).map(r => r.id));

        const validMarkers = (reqsRes || [])
          .filter(r => r.latitude && r.longitude)
          .map(r => ({
            id: r.id,
            lat: r.latitude,
            lng: r.longitude,
            urgency: r.urgency >= 4 ? 'high' : r.urgency >= 3 ? 'medium' : 'low',
            isNew: newestIds.has(r.id)
          }));
        setMapMarkers(validMarkers);

      } catch (err) {
        console.error('Failed to load dashboard data:', err);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  useEffect(() => {
    const ws = new WebSocket(WS_BASE);
    
    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        if (msg.type === 'NEW_REQUEST') {
          const req = msg.data;
          
          setData(prev => {
            const newStats = { ...prev.stats };
            newStats.totalRequests += 1;
            
            const newReq = {
              id: req.id,
              text: req.translated_text || req.raw_text,
              category: req.category,
              urgency: req.urgency >= 4 ? 'High' : req.urgency >= 3 ? 'Medium' : 'Low',
              time: formatTime(req.timestamp),
              language: req.language_detected
            };
            
            const newFeed = [newReq, ...prev.recentRequests].slice(0, 8);
            
            return {
              ...prev,
              stats: newStats,
              recentRequests: newFeed
            };
          });

          if (req.latitude && req.longitude) {
            setMapMarkers(prev => [{
              id: req.id,
              lat: req.latitude,
              lng: req.longitude,
              urgency: req.urgency >= 4 ? 'high' : req.urgency >= 3 ? 'medium' : 'low',
              isNew: true
            }, ...prev]);
          }
        }
      } catch (e) {
        console.error("WS error:", e);
      }
    };
    
    return () => ws.close();
  }, []);

  const toggleSimulator = async () => {
    try {
      const endpoint = simulatorRunning ? '/api/stop-simulator' : '/api/start-simulator';
      await fetch(`${API_BASE}${endpoint}`, { method: 'POST' });
      setSimulatorRunning(!simulatorRunning);
    } catch (e) {
      console.error(e);
    }
  };

  if (loading) {
    return <div className="flex h-full items-center justify-center">
      <div className="text-xl font-mono text-blue-400 animate-pulse flex items-center">
        <Activity className="mr-3 animate-spin" /> INITIALIZING SYSTEMS...
      </div>
    </div>;
  }

  const { stats, categoryData, languageData, topDistricts, recentRequests } = data;

  // Dark mode map styles array
  const darkMapStyles = [
    { elementType: 'geometry', stylers: [{ color: '#242f3e' }] },
    { elementType: 'labels.text.stroke', stylers: [{ color: '#242f3e' }] },
    { elementType: 'labels.text.fill', stylers: [{ color: '#746855' }] },
    { featureType: 'administrative.locality', elementType: 'labels.text.fill', stylers: [{ color: '#d59563' }] },
    { featureType: 'poi', elementType: 'labels.text.fill', stylers: [{ color: '#d59563' }] },
    { featureType: 'poi.park', elementType: 'geometry', stylers: [{ color: '#263c3f' }] },
    { featureType: 'poi.park', elementType: 'labels.text.fill', stylers: [{ color: '#6b9a76' }] },
    { featureType: 'road', elementType: 'geometry', stylers: [{ color: '#38414e' }] },
    { featureType: 'road', elementType: 'geometry.stroke', stylers: [{ color: '#212a37' }] },
    { featureType: 'road', elementType: 'labels.text.fill', stylers: [{ color: '#9ca5b3' }] },
    { featureType: 'road.highway', elementType: 'geometry', stylers: [{ color: '#746855' }] },
    { featureType: 'road.highway', elementType: 'geometry.stroke', stylers: [{ color: '#1f2835' }] },
    { featureType: 'road.highway', elementType: 'labels.text.fill', stylers: [{ color: '#f3d19c' }] },
    { featureType: 'transit', elementType: 'geometry', stylers: [{ color: '#2f3948' }] },
    { featureType: 'transit.station', elementType: 'labels.text.fill', stylers: [{ color: '#d59563' }] },
    { featureType: 'water', elementType: 'geometry', stylers: [{ color: '#17263c' }] },
    { featureType: 'water', elementType: 'labels.text.fill', stylers: [{ color: '#515c6d' }] },
    { featureType: 'water', elementType: 'labels.text.stroke', stylers: [{ color: '#17263c' }] }
  ];

  return (
    <div className="space-y-6 pb-10">
      {/* Header section */}
      <motion.div 
        initial={{ opacity: 0, scale: 0.98 }} animate={{ opacity: 1, scale: 1 }}
        className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6 premium-glass p-8 relative overflow-hidden"
      >
        <div className="absolute top-0 left-0 w-64 h-64 bg-red-500/10 rounded-full blur-3xl -translate-y-1/2 -translate-x-1/2 pointer-events-none"></div>
        <div className="relative z-10">
          <h2 className="text-3xl font-black text-white uppercase tracking-widest flex items-center">
            <ShieldAlert className="mr-4 text-red-500 animate-pulse h-8 w-8" />
            Live Threat & Priority Matrix
          </h2>
          <p className="text-sm font-medium text-slate-400 mt-2">Real-time infrastructure intelligence powered by Gemini AI</p>
        </div>
        <button 
          onClick={toggleSimulator}
          className={`mt-4 md:mt-0 px-8 py-4 text-xs font-bold tracking-widest uppercase rounded-xl flex items-center transition-all duration-300 relative z-10 ${
            simulatorRunning 
              ? 'bg-red-500/10 text-red-400 border border-red-500/30 hover:bg-red-500/20 shadow-[0_0_30px_rgba(239,68,68,0.3)]' 
              : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 hover:bg-emerald-500/20 shadow-[0_0_30px_rgba(16,185,129,0.3)]'
          }`}
        >
          {simulatorRunning ? (
            <><span className="h-3 w-3 rounded-full bg-red-500 animate-ping mr-3"></span> HALT STREAM</>
          ) : (
            <><Zap className="h-4 w-4 mr-2" /> ENGAGE 100x STREAM</>
          )}
        </button>
      </motion.div>

      {/* Stats Row */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {[
          { label: 'Total Intercepts', value: stats.totalRequests, icon: FileText, color: 'text-indigo-400', glow: 'shadow-[0_0_30px_rgba(79,70,229,0.2)]' },
          { label: 'Dialects Decoded', value: stats.languages, icon: Languages, color: 'text-emerald-400', glow: 'shadow-[0_0_30px_rgba(16,185,129,0.2)]' },
          { label: 'Sectors Monitored', value: stats.districts, icon: MapPin, color: 'text-purple-400', glow: 'shadow-[0_0_30px_rgba(168,85,247,0.2)]' },
          { label: 'Threat Level (Avg)', value: `${stats.avgUrgency} / 5.0`, icon: AlertTriangle, color: 'text-red-400', glow: 'shadow-[0_0_30px_rgba(239,68,68,0.2)]' },
        ].map((stat, i) => (
          <motion.div 
            initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }}
            key={i} 
            className={`premium-glass p-6 flex items-center border-l-2 border-l-transparent hover:border-l-indigo-500 transition-all duration-300 ${stat.glow}`}
          >
            <div className={`p-4 rounded-xl bg-white/[0.03] border border-white/[0.05] ${stat.color}`}>
              <stat.icon size={28} />
            </div>
            <div className="ml-5">
              <p className="text-[10px] font-mono text-slate-400 uppercase tracking-widest">{stat.label}</p>
              <p className="text-3xl font-black text-white mt-1 tracking-tight">{stat.value}</p>
            </div>
          </motion.div>
        ))}
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Live Terminal Feed */}
        <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.2 }} className="premium-glass lg:col-span-1 flex flex-col h-[600px]">
          <div className="px-6 py-4 border-b border-white/[0.05] flex justify-between items-center bg-white/[0.02]">
            <h3 className="text-xs font-mono font-bold text-slate-300 uppercase tracking-widest flex items-center">
              <Activity className="mr-2 h-4 w-4 text-emerald-500 animate-pulse" />
              Live Intercept Feed
            </h3>
          </div>
          <div className="flex-1 overflow-y-auto p-4 space-y-3 font-mono text-xs">
            <AnimatePresence>
              {recentRequests.map((req, i) => (
                <motion.div 
                  key={req.id || i}
                  initial={{ opacity: 0, height: 0, mb: 0 }}
                  animate={{ opacity: 1, height: 'auto', mb: 12 }}
                  exit={{ opacity: 0, height: 0, mb: 0 }}
                  className="p-3 bg-black/40 border border-white/[0.05] rounded shadow-inner overflow-hidden"
                >
                  <div className="flex justify-between items-start mb-2">
                    <span className={`px-2 py-0.5 rounded text-[9px] uppercase tracking-wider ${
                      req.urgency === 'High' ? 'bg-red-900/50 text-red-400 border border-red-800/50' :
                      req.urgency === 'Medium' ? 'bg-amber-900/50 text-amber-400 border border-amber-800/50' :
                      'bg-emerald-900/50 text-emerald-400 border border-emerald-800/50'
                    }`}>
                      Lvl {req.urgency === 'High' ? '3-CRITICAL' : req.urgency === 'Medium' ? '2-ELEVATED' : '1-STANDARD'}
                    </span>
                    <span className="text-slate-500">{req.time}</span>
                  </div>
                  <p className="text-slate-300 mb-2 truncate">{req.text}</p>
                  <div className="flex justify-between text-slate-500 text-[10px]">
                    <span>CAT: <span className="text-indigo-400">{req.category}</span></span>
                    <span>LANG: <span className="text-purple-400">{req.language}</span></span>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        </motion.div>

        {/* Live Radar Map */}
        <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.3 }} className="premium-glass lg:col-span-2 h-[600px] flex flex-col relative overflow-hidden">
          <div className="px-6 py-4 border-b border-white/[0.05] flex justify-between items-center bg-white/[0.02] absolute top-0 w-full z-10 backdrop-blur-md">
            <h3 className="text-xs font-mono font-bold text-slate-300 uppercase tracking-widest flex items-center">
              <Globe className="mr-2 h-4 w-4 text-indigo-400" />
              Live Sector Radar (API INTEGRATION)
            </h3>
            <span className="text-[9px] px-2 py-1 bg-indigo-500/20 text-indigo-300 rounded border border-indigo-500/30 font-mono">
              {mapMarkers.length} ACTIVE NODES
            </span>
          </div>
          <div className="flex-1 w-full h-full pt-14">
            <APIProvider apiKey={API_KEY}>
              <Map
                mapId="DEMO_MAP_ID"
                defaultCenter={{ lat: 20.5937, lng: 78.9629 }}
                defaultZoom={5}
                disableDefaultUI={true}
                styles={darkMapStyles}
              >
                {mapMarkers.map((marker, i) => (
                  <AdvancedMarker
                    key={marker.id || i}
                    position={{ lat: marker.lat, lng: marker.lng }}
                  >
                    <div className="relative flex items-center justify-center">
                      {marker.isNew && (
                        <>
                          <span className="absolute -inset-3 rounded-full bg-purple-500/50 animate-ping" />
                          <span className="absolute -inset-2 rounded-full bg-cyan-400/40 animate-pulse blur-sm" />
                          <span className="absolute -top-7 px-2 py-0.5 bg-gradient-to-r from-purple-600 to-indigo-600 text-white text-[9px] font-black tracking-widest uppercase rounded-full shadow-lg border border-purple-300/40 animate-bounce z-20">
                            NEW
                          </span>
                        </>
                      )}
                      <motion.div initial={{ scale: 0 }} animate={{ scale: marker.isNew ? 1.25 : 1 }} transition={{ delay: Math.min(i * 0.05, 1) }}>
                        <Pin
                          background={marker.isNew ? '#c084fc' : marker.urgency === 'high' ? '#ef4444' : marker.urgency === 'medium' ? '#f59e0b' : '#10b981'}
                          borderColor={marker.isNew ? '#ffffff' : 'rgba(255,255,255,0.2)'}
                          glyphColor={'#fff'}
                        />
                      </motion.div>
                    </div>
                  </AdvancedMarker>
                ))}
              </Map>
            </APIProvider>
          </div>
        </motion.div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="premium-glass p-6 h-[300px]">
            <h3 className="text-xs font-mono font-bold text-slate-400 uppercase tracking-widest mb-4">Anomaly Distribution by Sector</h3>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={categoryData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                <XAxis dataKey="name" stroke="#94a3b8" tick={{fill: '#94a3b8', fontSize: 10}} />
                <YAxis stroke="#94a3b8" tick={{fill: '#94a3b8', fontSize: 10}} />
                <RechartsTooltip 
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px' }}
                  itemStyle={{ color: '#e2e8f0' }}
                />
                <Bar dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="premium-glass p-6">
            <h3 className="text-xs font-mono font-bold text-slate-400 uppercase tracking-widest mb-4">Top Critical Zones</h3>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-slate-700/50 text-left">
                <thead>
                  <tr>
                    <th className="px-4 py-3 text-xs font-mono font-medium text-slate-500 uppercase tracking-wider">Sector Code</th>
                    <th className="px-4 py-3 text-xs font-mono font-medium text-slate-500 uppercase tracking-wider">Threat Score</th>
                    <th className="px-4 py-3 text-xs font-mono font-medium text-slate-500 uppercase tracking-wider">Infra Gap</th>
                    <th className="px-4 py-3 text-xs font-mono font-medium text-slate-500 uppercase tracking-wider">Primary Vector</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800 bg-transparent">
                  {topDistricts.map((district, idx) => (
                    <tr key={idx} className="hover:bg-slate-800/30 transition-colors">
                      <td className="px-4 py-4 whitespace-nowrap text-sm font-medium text-slate-200">{district.district_name}</td>
                      <td className="px-4 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <span className={`text-sm font-bold ${district.priority_score > 70 ? 'text-red-400' : 'text-amber-400'}`}>
                            {district.priority_score.toFixed(1)}
                          </span>
                          <div className="ml-3 w-16 bg-slate-800 rounded-full h-1.5">
                            <div 
                              className={`h-1.5 rounded-full ${district.priority_score > 70 ? 'bg-red-500' : 'bg-amber-500'}`} 
                              style={{ width: `${district.priority_score}%` }}
                            ></div>
                          </div>
                        </div>
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm font-mono text-slate-400">
                        {(district.infra_gap * 100).toFixed(0)}%
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-slate-300">
                        {district.top_issues && district.top_issues.length > 0 ? district.top_issues[0] : 'N/A'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
  );
}
