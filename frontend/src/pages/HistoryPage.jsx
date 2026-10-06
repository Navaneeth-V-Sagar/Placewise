import React, { useState, useEffect } from 'react';
import { History, Loader2, ArrowLeft, CheckCircle2, AlertTriangle, XCircle } from 'lucide-react';
import { getCandidateProgress } from '../services/api';

export default function HistoryPage({ candidateId, onBackToDashboard }) {
  const [progressData, setProgressData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadProgress();
  }, [candidateId]);

  const loadProgress = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getCandidateProgress(candidateId);
      setProgressData(data);
    } catch (err) {
      setError(err.message || 'Failed to load attempt history.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto py-20 px-4 text-center">
        <div className="glass-card p-12 flex flex-col items-center justify-center gap-4">
          <Loader2 className="w-10 h-10 animate-spin text-indigo-400" />
          <h2 className="text-xl font-bold text-white">Loading Assessment History...</h2>
        </div>
      </div>
    );
  }

  const attempts = progressData?.recent_attempts || [];

  return (
    <div className="max-w-4xl mx-auto py-8 px-4 sm:px-6 space-y-6">
      
      <div className="flex items-center justify-between">
        <button
          onClick={onBackToDashboard}
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-400 hover:text-white transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Dashboard</span>
        </button>

        <h1 className="text-xl font-bold text-white flex items-center gap-2">
          <History className="w-5 h-5 text-indigo-400" />
          Assessment History ({attempts.length})
        </h1>
      </div>

      {attempts.length === 0 ? (
        <div className="glass-card p-12 text-center text-slate-400 space-y-3">
          <p>No questions answered yet.</p>
          <button
            onClick={onBackToDashboard}
            className="px-5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold"
          >
            Start Practice
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {attempts.map((att) => {
            const isHigh = att.score >= 80;
            const isMed = att.score >= 50 && att.score < 80;
            return (
              <div key={att.id} className="glass-card p-6 space-y-3 border-slate-800">
                <div className="flex items-center justify-between flex-wrap gap-2">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold px-2 py-0.5 rounded-md bg-slate-800 text-white">
                      {att.skill}
                    </span>
                    <span className="text-xs text-indigo-300">
                      {att.topic}
                    </span>
                    <span className="text-[10px] text-slate-500">
                      • {att.difficulty}
                    </span>
                  </div>

                  <div className="flex items-center gap-2">
                    <span className={`text-sm font-extrabold ${
                      isHigh ? 'text-emerald-400' : isMed ? 'text-amber-400' : 'text-red-400'
                    }`}>
                      {att.score} / 100
                    </span>
                    <span className="text-xs text-slate-400">({att.correctness})</span>
                  </div>
                </div>

                <div className="text-xs text-slate-300">
                  <strong className="text-slate-400 block mb-1">Question:</strong>
                  {att.question}
                </div>

                <div className="p-3 rounded-lg bg-slate-950/80 border border-slate-800/80 text-xs text-slate-300">
                  <strong className="text-indigo-300 block mb-1">Feedback:</strong>
                  {att.feedback}
                </div>
              </div>
            );
          })}
        </div>
      )}

    </div>
  );
}
