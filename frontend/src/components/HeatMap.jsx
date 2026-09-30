import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { APIProvider, Map, AdvancedMarker, Pin } from '@vis.gl/react-google-maps';
import { Globe, AlertTriangle, Search, Filter } from 'lucide-react';
import { getRequests } from '../services/api';

const API_KEY = import.meta.env.VITE_GOOGLE_MAPS_API_KEY || '';

export default function HeatMap() {
  const [markers, setMarkers] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [selectedUrgency, setSelectedUrgency] = useState('All');
  const [activeMarker, setActiveMarker] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchMarkers() {
      try {
        const requests = await getRequests();
        const validMarkers = (requests || [])
          .filter(r => r.latitude && r.longitude)
          .map(r => ({
            id: r.id,
            lat: parseFloat(r.latitude),
            lng: parseFloat(r.longitude),
            urgency: r.urgency >= 4 ? 'high' : r.urgency >= 3 ? 'medium' : 'low',
            category: r.category,
            title: r.translated_text || r.raw_text,
            district: r.location_district,
            state: r.location_state,
            language: r.language_detected
          }));
        setMarkers(validMarkers);
      } catch (err) {
        console.error("Failed to load map data", err);
      } finally {
        setLoading(false);
      }
    }
    fetchMarkers();
  }, []);

  const categories = ['All', ...new Set(markers.map(m => m.category))];

  const getPinColor = (urgency) => {
    switch(urgency) {
      case 'high': return '#ef4444'; // Red
      case 'medium': return '#f59e0b'; // Amber
      default: return '#10b981'; // Green
    }
  };

  const filteredMarkers = markers.filter(m => {
    if (selectedCategory !== 'All' && m.category !== selectedCategory) return false;
    if (selectedUrgency !== 'All' && m.urgency !== selectedUrgency) return false;
    return true;
  });

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

  if (!API_KEY) {
    return (
      <div className="flex flex-col items-center justify-center h-full premium-glass p-10 text-center animate-fade-in-up relative overflow-hidden">
        <div className="absolute top-0 right-0 w-64 h-64 bg-red-500/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/3"></div>
        <motion.div 
          initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ type: 'spring', bounce: 0.5 }}
          className="bg-white/[0.03] p-6 rounded-full mb-6 border border-white/[0.05]"
        >
          <AlertTriangle className="w-16 h-16 text-slate-500" />
        </motion.div>
        <h3 className="text-3xl font-black text-white mb-4 tracking-tighter">Live Radar Offline</h3>
        <p className="text-slate-400 max-w-lg mb-8 leading-relaxed">
          Geospatial mapping requires the VITE_GOOGLE_MAPS_API_KEY environment variable. 
          The .env configuration is currently missing or not loaded correctly by Vite.
        </p>
        
        {/* Offline Fallback Data */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}
          className="w-full max-w-2xl bg-black/40 border border-white/[0.1] rounded-2xl p-6 text-left"
        >
          <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-4">
            {markers.length} Raw Signals Detected (Geospatial Render Disabled)
          </p>
          
          <div className="grid grid-cols-3 gap-4 mb-6">
            <div className="bg-red-500/10 border border-red-500/20 p-4 rounded-xl text-center">
              <div className="text-2xl font-black text-red-400">{markers.filter(m => m.urgency === 'high').length}</div>
              <div className="text-[10px] uppercase font-bold text-red-500 mt-1">Critical</div>
            </div>
            <div className="bg-amber-500/10 border border-amber-500/20 p-4 rounded-xl text-center">
              <div className="text-2xl font-black text-amber-400">{markers.filter(m => m.urgency === 'medium').length}</div>
              <div className="text-[10px] uppercase font-bold text-amber-500 mt-1">Elevated</div>
            </div>
            <div className="bg-emerald-500/10 border border-emerald-500/20 p-4 rounded-xl text-center">
              <div className="text-2xl font-black text-emerald-400">{markers.filter(m => m.urgency === 'low').length}</div>
              <div className="text-[10px] uppercase font-bold text-emerald-500 mt-1">Standard</div>
            </div>
          </div>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full space-y-4 pb-10">
      {/* Header & Controls */}
      <motion.div 
        initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} 
        className="premium-glass p-6 flex flex-col sm:flex-row justify-between items-start sm:items-center relative overflow-hidden"
      >
        <div className="absolute top-0 left-0 w-64 h-64 bg-indigo-500/10 rounded-full blur-3xl -translate-y-1/2 -translate-x-1/2 pointer-events-none"></div>
        <div className="relative z-10 flex items-center">
          <Globe className="h-8 w-8 text-indigo-400 mr-4 animate-[spin_10s_linear_infinite]" />
          <div>
            <h2 className="text-2xl font-black text-white tracking-widest uppercase">Live Sector Radar</h2>
            <p className="text-[10px] font-mono text-slate-400 mt-1 uppercase tracking-widest">Global Geospatial Threat Visualization</p>
          </div>
        </div>
        
        <div className="flex space-x-4 mt-6 sm:mt-0 relative z-10">
          <div className="relative">
            <Filter className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
            <select 
              className="bg-black/60 border border-white/[0.1] text-slate-300 text-xs font-bold tracking-widest uppercase rounded-xl focus:ring-indigo-500 focus:border-indigo-500 block pl-10 pr-8 py-3 appearance-none transition-all hover:border-white/[0.2]"
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
            >
              <option value="All">All Sectors</option>
              {categories.map(c => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>
          <div className="relative">
            <AlertTriangle className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
            <select 
              className="bg-black/60 border border-white/[0.1] text-slate-300 text-xs font-bold tracking-widest uppercase rounded-xl focus:ring-indigo-500 focus:border-indigo-500 block pl-10 pr-8 py-3 appearance-none transition-all hover:border-white/[0.2]"
              value={selectedUrgency}
              onChange={(e) => setSelectedUrgency(e.target.value)}
            >
              <option value="All">All Threats</option>
              <option value="high">Critical Only</option>
              <option value="medium">Elevated Only</option>
              <option value="low">Standard Only</option>
            </select>
          </div>
        </div>
      </motion.div>

      {/* Interactive Map */}
      <motion.div 
        initial={{ opacity: 0, scale: 0.98 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.1 }}
        className="flex-1 premium-glass relative overflow-hidden rounded-2xl border border-white/[0.05]"
      >
        <APIProvider apiKey={API_KEY}>
          <Map
            mapId="DEMO_MAP_ID"
            defaultCenter={{ lat: 20.5937, lng: 78.9629 }}
            defaultZoom={5}
            disableDefaultUI={false}
            styles={darkMapStyles}
          >
            {filteredMarkers.map((marker, i) => (
              <AdvancedMarker
                key={marker.id}
                position={{lat: marker.lat, lng: marker.lng}}
                onClick={() => setActiveMarker(activeMarker === marker.id ? null : marker.id)}
              >
                <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ delay: i * 0.05, type: 'spring' }}>
                  <Pin
                    background={getPinColor(marker.urgency)}
                    borderColor={'rgba(255,255,255,0.2)'}
                    glyphColor={'#fff'}
                  />
                </motion.div>
              </AdvancedMarker>
            ))}
          </Map>
        </APIProvider>

        {/* Info panel for selected marker */}
        <AnimatePresence>
          {activeMarker && (() => {
            const m = markers.find(m => m.id === activeMarker);
            if (!m) return null;
            return (
              <motion.div 
                initial={{ opacity: 0, x: -20, y: 10 }} 
                animate={{ opacity: 1, x: 0, y: 0 }} 
                exit={{ opacity: 0, x: -20, y: 10 }}
                className="absolute bottom-6 left-6 premium-glass p-6 max-w-sm z-10 border border-white/[0.1] shadow-2xl backdrop-blur-3xl"
              >
                <button onClick={() => setActiveMarker(null)} className="absolute top-4 right-4 text-slate-500 hover:text-white transition-colors">✕</button>
                <h4 className="font-black text-white pr-6 text-xl tracking-tight">{m.district}</h4>
                <p className="text-xs font-bold text-slate-500 tracking-widest uppercase mb-3">{m.state}</p>
                <p className="text-sm text-slate-300 mb-4 leading-relaxed bg-black/30 p-3 rounded-lg border border-white/[0.05]">{m.title}</p>
                <div className="flex flex-wrap gap-2">
                  <span className="text-[10px] font-bold uppercase tracking-widest bg-indigo-500/20 border border-indigo-500/30 text-indigo-300 px-2.5 py-1 rounded-md">{m.category}</span>
                  <span className={`text-[10px] font-bold uppercase tracking-widest border px-2.5 py-1 rounded-md ${
                    m.urgency === 'high' ? 'bg-red-500/20 border-red-500/30 text-red-400' :
                    m.urgency === 'medium' ? 'bg-amber-500/20 border-amber-500/30 text-amber-400' :
                    'bg-emerald-500/20 border-emerald-500/30 text-emerald-400'
                  }`}>{m.urgency}</span>
                  <span className="text-[10px] font-bold uppercase tracking-widest bg-white/[0.05] border border-white/[0.1] text-slate-400 px-2.5 py-1 rounded-md">{m.language}</span>
                </div>
              </motion.div>
            );
          })()}
        </AnimatePresence>
      </motion.div>
    </div>
  );
}
