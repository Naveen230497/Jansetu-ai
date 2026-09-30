import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { FileText, Download, Loader2, CheckCircle, FileOutput, RefreshCw } from 'lucide-react';
import { generateBrief, getStats, recalculate } from '../services/api';

export default function PolicyBrief() {
  const [isGenerating, setIsGenerating] = useState(false);
  const [briefGenerated, setBriefGenerated] = useState(false);
  const [pdfUrl, setPdfUrl] = useState(null);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState(null);

  useEffect(() => {
    getStats().then(setStats).catch(console.error);
  }, []);

  const handleGenerate = async () => {
    setIsGenerating(true);
    setError(null);

    try {
      await recalculate();
      const blob = await generateBrief();
      window.__lastBriefType = blob.type;
      const url = URL.createObjectURL(blob);
      setPdfUrl(url);
      setBriefGenerated(true);
    } catch (err) {
      console.error('Failed to generate brief:', err);
      setError('Failed to generate policy brief. Please ensure the backend is running.');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleDownload = () => {
    if (pdfUrl) {
      const isHtml = window.__lastBriefType === 'text/html';
      const ext = isHtml ? 'html' : 'pdf';
      const a = document.createElement('a');
      a.href = pdfUrl;
      a.download = `JanSetu_Policy_Brief_${new Date().toISOString().split('T')[0]}.${ext}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    }
  };

  const handleReset = () => {
    setBriefGenerated(false);
    setPdfUrl(null);
  };

  return (
    <div className="max-w-5xl mx-auto space-y-8 pb-10">
      <motion.div 
        initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} 
        className="flex flex-col sm:flex-row justify-between items-start sm:items-center bg-white/[0.03] border border-white/[0.05] rounded-2xl p-8 shadow-2xl relative overflow-hidden"
      >
        <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-500/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/3"></div>
        <div className="relative z-10">
          <h2 className="text-3xl font-black text-white tracking-tight">AI Intelligence Brief</h2>
          <p className="text-sm font-medium text-slate-400 mt-2">
            Synthesize citizen feedback into actionable policy recommendations.
          </p>
        </div>
        <div className="flex space-x-3 mt-6 sm:mt-0 relative z-10">
          {briefGenerated && (
            <button
              onClick={handleReset}
              className="inline-flex items-center px-5 py-2.5 bg-white/[0.05] hover:bg-white/[0.1] border border-white/[0.1] text-sm font-semibold rounded-xl text-slate-300 transition-all"
            >
              <RefreshCw className="mr-2 h-4 w-4" /> Reset
            </button>
          )}
          <button
            onClick={briefGenerated ? handleDownload : handleGenerate}
            disabled={isGenerating}
            className={`inline-flex items-center px-6 py-2.5 border border-transparent text-sm font-semibold rounded-xl text-white shadow-[0_0_20px_rgba(79,70,229,0.4)] transition-all ${
              isGenerating ? 'bg-indigo-600/50 cursor-not-allowed' : 'bg-indigo-600 hover:bg-indigo-500 hover:shadow-[0_0_30px_rgba(79,70,229,0.6)]'
            }`}
          >
            {isGenerating ? (
              <><Loader2 className="animate-spin -ml-1 mr-2 h-4 w-4" /> Processing AI Models...</>
            ) : briefGenerated ? (
              <><Download className="-ml-1 mr-2 h-4 w-4" /> Download Brief</>
            ) : (
              <><FileOutput className="-ml-1 mr-2 h-4 w-4" /> Generate Intelligence Brief</>
            )}
          </button>
        </div>
      </motion.div>

      {error && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="bg-red-500/10 border border-red-500/20 rounded-xl p-4 text-red-400 text-sm flex items-center">
          <Loader2 className="h-4 w-4 mr-2" /> {error}
        </motion.div>
      )}

      {!briefGenerated && !isGenerating && (
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-3">
          {[
            { label: 'REQUESTS TO ANALYZE', value: stats?.total_requests || 0 },
            { label: 'LANGUAGES COVERED', value: Object.keys(stats?.languages || {}).length || 0 },
            { label: 'ISSUE CATEGORIES', value: Object.keys(stats?.categories || {}).length || 0 }
          ].map((s, i) => (
            <motion.div 
              key={i}
              initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }}
              className="bg-white/[0.02] border border-white/[0.05] rounded-2xl p-8 text-center hover:bg-white/[0.04] transition-colors"
            >
              <div className="text-4xl font-black text-indigo-400 mb-2">{s.value}</div>
              <div className="text-xs font-bold text-slate-500 tracking-widest">{s.label}</div>
            </motion.div>
          ))}
        </div>
      )}

      {/* State views... */}
      <div className="min-h-[500px]">
        {isGenerating ? (
          <div className="h-[400px] flex flex-col items-center justify-center space-y-6">
            <div className="relative">
              <div className="absolute inset-0 bg-indigo-500 rounded-full blur-xl animate-pulse opacity-50"></div>
              <Loader2 className="h-16 w-16 text-indigo-400 animate-spin relative z-10" />
            </div>
            <div className="text-center">
              <h3 className="text-xl font-bold text-white mb-2">Neural Synthesis Active</h3>
              <p className="text-slate-400 max-w-sm">
                Aggregating district priorities and formatting executive summary...
              </p>
            </div>
          </div>
        ) : briefGenerated && pdfUrl ? (
          <motion.div initial={{ opacity: 0, scale: 0.98 }} animate={{ opacity: 1, scale: 1 }} className="h-[700px] premium-glass rounded-2xl overflow-hidden shadow-[0_0_50px_rgba(0,0,0,0.5)]">
            <iframe src={pdfUrl} className="w-full h-full border-0" title="Generated Policy Brief" />
          </motion.div>
        ) : (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3 }} className="h-[400px] flex flex-col items-center justify-center bg-white/[0.01] border border-dashed border-white/[0.1] rounded-2xl">
            <FileText className="h-16 w-16 text-slate-600 mb-4" />
            <h3 className="text-lg font-bold text-slate-300 mb-2">No Brief Generated Yet</h3>
            <p className="text-slate-500 max-w-md text-center text-sm">
              Click the button above to trigger the Gemini AI pipeline. It will analyze all classified citizen feedback and generate a structured PDF.
            </p>
          </motion.div>
        )}
      </div>
    </div>
  );
}
