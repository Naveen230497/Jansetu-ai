import React, { useState, useRef } from 'react';
import { Mic, Square, Send, Loader2, CheckCircle2, AlertCircle } from 'lucide-react';
import { submitText, submitVoice } from '../services/api';

export default function VoiceRecorder() {
  const [text, setText] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);

  const handleTextSubmit = async () => {
    if (!text.trim()) return;
    setIsProcessing(true);
    setError(null);
    setResult(null);

    try {
      const response = await submitText(text);
      setResult({
        detectedLanguage: response.classification?.language || 'Unknown',
        translation: response.classification?.translated_text || text,
        category: response.classification?.category || 'Unknown',
        urgency: response.classification?.urgency >= 4 ? 'High' : response.classification?.urgency >= 3 ? 'Medium' : 'Low',
        district: response.classification?.district || 'Unknown',
        state: response.classification?.state || 'Unknown',
        id: response.id
      });
      setText('');
    } catch (err) {
      console.error('Error submitting text:', err);
      setError('Failed to process your feedback. Please ensure the backend is running.');
    } finally {
      setIsProcessing(false);
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunksRef.current.push(e.data);
        }
      };

      mediaRecorder.onstop = async () => {
        stream.getTracks().forEach(track => track.stop());
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
        const file = new File([blob], 'recording.webm', { type: 'audio/webm' });

        setIsProcessing(true);
        setError(null);
        try {
          const response = await submitVoice(file);
          setResult({
            detectedLanguage: response.classification?.language || 'Unknown',
            translation: response.classification?.translated_text || 'Translation unavailable',
            category: response.classification?.category || 'Unknown',
            urgency: response.classification?.urgency >= 4 ? 'High' : response.classification?.urgency >= 3 ? 'Medium' : 'Low',
            district: response.classification?.district || 'Unknown',
            state: response.classification?.state || 'Unknown',
            id: response.id
          });
        } catch (err) {
          console.error('Error submitting voice:', err);
          setError('Failed to process voice feedback. Please ensure backend is running.');
        } finally {
          setIsProcessing(false);
        }
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (err) {
      console.error('Error accessing microphone:', err);
      setError('Microphone access denied or unavailable.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const toggleRecording = () => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 pb-10">
      <div className="text-center mb-10">
        <h2 className="text-3xl font-black text-white uppercase tracking-widest mb-4">Citizen Feedback Portal</h2>
        <p className="text-slate-400 font-medium max-w-2xl mx-auto">
          Speak or type your civic issues in any Indian language. Our AI will analyze and route it to the right department.
        </p>
      </div>

      <div className="premium-glass overflow-hidden rounded-2xl border border-white/[0.05] shadow-2xl relative">
        <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-indigo-500 via-purple-500 to-emerald-500"></div>
        <div className="p-8">
          <label htmlFor="feedback" className="block text-xs font-bold text-slate-500 uppercase tracking-widest mb-4">
            Record Voice or Type (Any Language)
          </label>
          <div className="relative">
            <textarea
              id="feedback"
              name="feedback"
              rows={5}
              className="block w-full bg-black/40 border border-white/[0.1] rounded-xl text-white placeholder-slate-600 focus:ring-indigo-500 focus:border-indigo-500 sm:text-lg p-5 resize-none transition-all focus:bg-black/60 outline-none"
              placeholder="E.g., हमारे गाँव में पिछले तीन महीने से बिजली नहीं आ रही है..."
              value={text}
              onChange={(e) => setText(e.target.value)}
              disabled={isRecording || isProcessing}
            />
            
            <div className="absolute bottom-4 right-4 flex space-x-3">
              <button
                type="button"
                onClick={toggleRecording}
                disabled={isProcessing}
                className={`inline-flex items-center justify-center rounded-xl p-4 shadow-lg focus:outline-none transition-all duration-300 ${
                  isRecording 
                    ? 'bg-red-500/20 text-red-400 border border-red-500/50 animate-pulse shadow-[0_0_20px_rgba(239,68,68,0.3)]' 
                    : 'bg-white/[0.05] text-slate-300 border border-white/[0.1] hover:bg-white/[0.1] hover:text-white'
                }`}
              >
                {isRecording ? <Square size={24} fill="currentColor" /> : <Mic size={24} />}
              </button>
            </div>
          </div>
        </div>
        
        <div className="px-8 py-5 bg-black/40 border-t border-white/[0.05] flex flex-col sm:flex-row justify-between items-center space-y-4 sm:space-y-0">
          <div className="text-sm text-slate-400 flex items-center font-mono">
            {isRecording && (
              <>
                <span className="h-3 w-3 bg-red-500 rounded-full animate-ping mr-3 shadow-[0_0_10px_rgba(239,68,68,1)]"></span>
                <span className="text-red-400">Recording... Speak clearly</span>
              </>
            )}
          </div>
          <button
            onClick={handleTextSubmit}
            disabled={(!text.trim() && !isRecording) || isProcessing || isRecording}
            className={`inline-flex items-center px-8 py-3 text-sm font-black tracking-widest uppercase rounded-xl shadow-lg transition-all duration-300 ${
              (!text.trim() && !isRecording) || isProcessing || isRecording
                ? 'bg-white/[0.05] text-slate-500 cursor-not-allowed border border-white/[0.05]'
                : 'bg-indigo-600 text-white hover:bg-indigo-500 shadow-[0_0_20px_rgba(79,70,229,0.4)] border border-indigo-400/50'
            }`}
          >
            {isProcessing ? (
              <>
                <Loader2 className="animate-spin -ml-1 mr-3 h-5 w-5" />
                Processing with Gemini...
              </>
            ) : (
              <>
                <Send className="-ml-1 mr-3 h-5 w-5" />
                Submit Feedback
              </>
            )}
          </button>
        </div>
      </div>

      {/* Error display */}
      {error && (
        <div className="premium-glass bg-red-500/10 border border-red-500/30 rounded-xl p-5 flex items-center">
          <AlertCircle className="text-red-400 mr-3 h-6 w-6" />
          <p className="text-red-400 text-sm font-medium">{error}</p>
        </div>
      )}

      {/* AI Processing Result Card */}
      {result && (
        <div className="mt-8 premium-glass rounded-xl overflow-hidden border border-emerald-500/30 shadow-[0_0_30px_rgba(16,185,129,0.1)] relative">
          <div className="absolute top-0 right-0 w-64 h-64 bg-emerald-500/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2 pointer-events-none"></div>
          <div className="bg-emerald-500/10 px-8 py-5 border-b border-emerald-500/20 flex items-center relative z-10">
            <CheckCircle2 className="h-7 w-7 text-emerald-400 mr-3" />
            <h3 className="text-xl font-black text-emerald-400 tracking-widest uppercase">Feedback Processed</h3>
          </div>
          
          <div className="p-8 relative z-10">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div>
                <h4 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-3">AI Translation ({result.detectedLanguage})</h4>
                <p className="text-white bg-black/40 p-4 rounded-xl border border-white/[0.05] italic leading-relaxed text-lg shadow-inner">"{result.translation}"</p>
              </div>
              
              <div className="grid grid-cols-2 gap-6">
                <div className="bg-white/[0.02] p-4 rounded-xl border border-white/[0.05]">
                  <h4 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-2">Category</h4>
                  <span className="inline-flex items-center px-3 py-1 rounded-md text-xs font-bold uppercase tracking-widest bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">
                    {result.category}
                  </span>
                </div>
                <div className="bg-white/[0.02] p-4 rounded-xl border border-white/[0.05]">
                  <h4 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-2">Urgency</h4>
                  <span className={`inline-flex items-center px-3 py-1 rounded-md text-xs font-bold uppercase tracking-widest border ${
                    result.urgency === 'High' ? 'bg-red-500/20 text-red-400 border-red-500/30' :
                    result.urgency === 'Medium' ? 'bg-amber-500/20 text-amber-400 border-amber-500/30' :
                    'bg-emerald-500/20 text-emerald-400 border-emerald-500/30'
                  }`}>
                    {result.urgency}
                  </span>
                </div>
                <div className="bg-white/[0.02] p-4 rounded-xl border border-white/[0.05] col-span-2">
                  <h4 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-2">Routed To</h4>
                  <p className="text-lg font-black text-white">{result.district}, {result.state}</p>
                </div>
              </div>
            </div>
            
            <div className="mt-8 pt-6 border-t border-white/[0.05]">
              <p className="text-xs text-slate-500 text-center font-mono uppercase tracking-widest">
                Data synthesized and routed to live anomaly radar. (ID: #{result.id})
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
