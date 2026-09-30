import React from 'react';
import { Routes, Route, Link, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { LayoutDashboard, Map, MapPin, Mic, FileText, Menu, X, Activity, Hexagon } from 'lucide-react';
import Dashboard from './components/Dashboard';
import HeatMap from './components/HeatMap';
import DistrictDetail from './components/DistrictDetail';
import VoiceRecorder from './components/VoiceRecorder';
import PolicyBrief from './components/PolicyBrief';

export default function App() {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = React.useState(false);
  const location = useLocation();

  const navItems = [
    { path: '/', label: 'Command Center', icon: LayoutDashboard },
    { path: '/heatmap', label: 'Live Radar', icon: Map },
    { path: '/districts', label: 'Sector Analysis', icon: MapPin },
    { path: '/submit', label: 'Input Data', icon: Mic },
    { path: '/policy', label: 'Intelligence Brief', icon: FileText },
  ];

  return (
    <div className="flex h-screen overflow-hidden bg-[#030712] font-sans">
      {/* Cinematic Glowing Background Orbs */}
      <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] rounded-full bg-indigo-600/10 blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] rounded-full bg-emerald-600/10 blur-[120px] pointer-events-none" />

      {/* Sidebar - Desktop */}
      <aside className="hidden w-72 m-4 mr-0 rounded-2xl premium-glass md:flex flex-col relative z-20">
        <div className="flex h-24 items-center px-8 border-b border-white/[0.05]">
          <Hexagon className="h-8 w-8 text-indigo-400 mr-3 animate-[spin_10s_linear_infinite]" />
          <h1 className="text-2xl font-black tracking-tighter text-white">
            JAN<span className="text-indigo-400">SETU</span>
          </h1>
        </div>
        
        <nav className="flex-1 space-y-2 px-4 py-8">
          {navItems.map((item) => {
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                className="relative group flex items-center px-4 py-3.5 rounded-xl transition-all duration-300"
              >
                {isActive && (
                  <motion.div
                    layoutId="activeTab"
                    className="absolute inset-0 bg-white/[0.08] rounded-xl border border-white/[0.1]"
                    transition={{ type: "spring", stiffness: 300, damping: 30 }}
                  />
                )}
                <item.icon
                  className={`mr-4 h-5 w-5 flex-shrink-0 relative z-10 transition-colors duration-300 ${
                    isActive ? 'text-indigo-400' : 'text-slate-500 group-hover:text-slate-300'
                  }`}
                />
                <span className={`text-sm font-medium relative z-10 ${
                  isActive ? 'text-white' : 'text-slate-400 group-hover:text-slate-200'
                }`}>
                  {item.label}
                </span>
              </Link>
            );
          })}
        </nav>
        
        <div className="p-6 border-t border-white/[0.05]">
          <div className="bg-black/40 rounded-xl p-4 flex items-center space-x-4 border border-white/[0.05]">
            <div className="relative flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
            </div>
            <div className="flex flex-col">
              <span className="text-[10px] font-mono text-slate-500 uppercase tracking-widest">Core Engine</span>
              <span className="text-xs font-bold text-slate-200">Gemini 3.8 Active</span>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 overflow-hidden relative z-10 flex flex-col p-4 md:p-8">
        <div className="w-full h-full premium-glass overflow-y-auto overflow-x-hidden p-6 md:p-10 relative">
          <AnimatePresence mode="wait">
            <Routes location={location} key={location.pathname}>
              <Route path="/" element={
                <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }} transition={{ duration: 0.3 }}>
                  <Dashboard />
                </motion.div>
              } />
              <Route path="/heatmap" element={
                <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0 }} transition={{ duration: 0.3 }} className="h-full">
                  <HeatMap />
                </motion.div>
              } />
              <Route path="/districts" element={
                <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }} transition={{ duration: 0.3 }}>
                  <DistrictDetail />
                </motion.div>
              } />
              <Route path="/submit" element={
                <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }} transition={{ duration: 0.3 }}>
                  <VoiceRecorder />
                </motion.div>
              } />
              <Route path="/policy" element={
                <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }} transition={{ duration: 0.3 }}>
                  <PolicyBrief />
                </motion.div>
              } />
            </Routes>
          </AnimatePresence>
        </div>
      </main>
    </div>
  );
}
