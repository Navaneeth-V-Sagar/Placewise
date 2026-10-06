import React from 'react';
import { Compass, Sparkles, Activity, RotateCcw } from 'lucide-react';

export default function Navbar({ currentView, setView, candidateId, healthStatus, onReset }) {
  return (
    <header className="border-b border-slate-800/80 bg-slate-950/70 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        
        {/* Logo */}
        <div 
          onClick={() => setView(candidateId ? 'dashboard' : 'setup')}
          className="flex items-center gap-3 cursor-pointer group"
        >
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-indigo-700 flex items-center justify-center shadow-lg shadow-indigo-500/20 group-hover:scale-105 transition-transform">
            <Compass className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-lg tracking-tight text-white group-hover:text-indigo-300 transition-colors">
                PLACEWISE
              </span>
              <span className="text-[10px] font-semibold uppercase px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                Adaptive AI
              </span>
            </div>
            <p className="text-[11px] text-slate-400">Intelligent Placement Preparation</p>
          </div>
        </div>

        {/* Navigation buttons */}
        {candidateId && (
          <nav className="flex items-center gap-1 bg-slate-900/90 p-1 rounded-xl border border-slate-800 text-sm">
            <button
              onClick={() => setView('dashboard')}
              className={`px-3.5 py-1.5 rounded-lg font-medium transition-all ${
                currentView === 'dashboard'
                  ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              Dashboard
            </button>
            <button
              onClick={() => setView('practice')}
              className={`px-3.5 py-1.5 rounded-lg font-medium transition-all ${
                currentView === 'practice'
                  ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              Adaptive Practice
            </button>
            <button
              onClick={() => setView('history')}
              className={`px-3.5 py-1.5 rounded-lg font-medium transition-all ${
                currentView === 'history'
                  ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              Attempt History
            </button>
          </nav>
        )}

        {/* System & Model Status Badge */}
        <div className="flex items-center gap-3">
          <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs">
            <span className={`w-2 h-2 rounded-full ${
              healthStatus?.ollama?.status === 'ready' ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400'
            }`} />
            <span className="text-slate-400">Model:</span>
            <span className="font-mono font-medium text-indigo-300">qwen3:4b</span>
          </div>

          {candidateId && (
            <button
              onClick={onReset}
              title="Start New Profile Analysis"
              className="p-2 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors"
            >
              <RotateCcw className="w-4 h-4" />
            </button>
          )}
        </div>

      </div>
    </header>
  );
}
