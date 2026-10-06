import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import SetupPage from './pages/SetupPage';
import DashboardPage from './pages/DashboardPage';
import PracticePage from './pages/PracticePage';
import ResultPage from './pages/ResultPage';
import HistoryPage from './pages/HistoryPage';
import { checkHealth, getCandidateProgress } from './services/api';

export default function App() {
  const [currentView, setCurrentView] = useState('setup'); // 'setup', 'dashboard', 'practice', 'result', 'history'
  const [candidateId, setCandidateId] = useState(null);
  const [analysisData, setAnalysisData] = useState(null);
  const [evaluationData, setEvaluationData] = useState(null);
  const [healthStatus, setHealthStatus] = useState(null);

  useEffect(() => {
    // Probe backend health on mount
    checkHealth()
      .then(data => setHealthStatus(data))
      .catch(err => console.warn('Health check warning:', err.message));
  }, []);

  const handleAnalysisComplete = (data) => {
    setAnalysisData(data);
    setCandidateId(data.candidate_id);
    setCurrentView('dashboard');
  };

  const handleEvaluationComplete = (evalData) => {
    setEvaluationData(evalData);
    setCurrentView('result');
    // Refresh background progress
    refreshCandidateProgress(candidateId);
  };

  const refreshCandidateProgress = async (cid) => {
    if (!cid) return;
    try {
      const progress = await getCandidateProgress(cid);
      setAnalysisData(prev => ({
        ...prev,
        readiness: progress.readiness,
        skill_gaps: progress.skill_gaps,
        recommended_focus: progress.current_recommendation,
      }));
    } catch (e) {
      console.error('Failed to sync progress:', e);
    }
  };

  const handleReset = () => {
    setCandidateId(null);
    setAnalysisData(null);
    setEvaluationData(null);
    setCurrentView('setup');
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      
      <Navbar
        currentView={currentView}
        setView={setCurrentView}
        candidateId={candidateId}
        healthStatus={healthStatus}
        onReset={handleReset}
      />

      <main className="flex-1">
        {currentView === 'setup' && (
          <SetupPage onAnalysisComplete={handleAnalysisComplete} />
        )}

        {currentView === 'dashboard' && analysisData && (
          <DashboardPage
            analysisData={analysisData}
            onStartPractice={() => setCurrentView('practice')}
            onRefreshProgress={() => refreshCandidateProgress(candidateId)}
          />
        )}

        {currentView === 'practice' && candidateId && (
          <PracticePage
            candidateId={candidateId}
            onEvaluationComplete={handleEvaluationComplete}
            onBackToDashboard={() => setCurrentView('dashboard')}
          />
        )}

        {currentView === 'result' && evaluationData && (
          <ResultPage
            evaluationData={evaluationData}
            onNextQuestion={() => setCurrentView('practice')}
            onBackToDashboard={() => setCurrentView('dashboard')}
          />
        )}

        {currentView === 'history' && candidateId && (
          <HistoryPage
            candidateId={candidateId}
            onBackToDashboard={() => setCurrentView('dashboard')}
          />
        )}
      </main>

      <footer className="border-t border-slate-800/80 py-6 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>PLACEWISE • AI-Powered Adaptive Placement Preparation</span>
          <span className="font-mono text-slate-600">Local inference via Ollama (qwen3:4b) + FastAPI + SQLite</span>
        </div>
      </footer>

    </div>
  );
}
