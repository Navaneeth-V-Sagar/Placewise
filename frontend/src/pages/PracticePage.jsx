import React, { useState, useEffect } from 'react';
import { Sparkles, Send, Loader2, ArrowLeft, Lightbulb, Code2, AlertCircle } from 'lucide-react';
import { getNextQuestion, evaluateAnswer } from '../services/api';

export default function PracticePage({ candidateId, onEvaluationComplete, onBackToDashboard }) {
  const [questionData, setQuestionData] = useState(null);
  const [answer, setAnswer] = useState('');
  const [loadingQuestion, setLoadingQuestion] = useState(true);
  const [evaluating, setEvaluating] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchQuestion();
  }, [candidateId]);

  const fetchQuestion = async () => {
    try {
      setLoadingQuestion(true);
      setError(null);
      const data = await getNextQuestion(candidateId);
      setQuestionData(data);
      setAnswer('');
    } catch (err) {
      setError(err.message || 'Failed to load adaptive question.');
    } finally {
      setLoadingQuestion(false);
    }
  };

  const handleEvaluate = async (e) => {
    if (e) e.preventDefault();
    if (!answer.trim()) {
      setError('Please type your answer before submitting.');
      return;
    }
    if (!questionData) return;

    try {
      setEvaluating(true);
      setError(null);
      const evalResponse = await evaluateAnswer(candidateId, questionData.question_id, answer);
      onEvaluationComplete(evalResponse);
    } catch (err) {
      setError(err.message || 'Failed to evaluate answer.');
      setEvaluating(false);
    }
  };

  const handleKeyDown = (e) => {
    // Ctrl+Enter or Cmd+Enter to submit
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      handleEvaluate();
    }
  };

  if (loadingQuestion) {
    return (
      <div className="max-w-3xl mx-auto py-20 px-4 text-center">
        <div className="glass-card p-12 flex flex-col items-center justify-center gap-4">
          <Loader2 className="w-10 h-10 animate-spin text-indigo-400" />
          <h2 className="text-xl font-bold text-white">Generating Targeted Adaptive Question...</h2>
          <p className="text-sm text-slate-400 max-w-md">
            The adaptive planner is analyzing your priority gaps and formulating a scenario-based question with Qwen3:4b.
          </p>
        </div>
      </div>
    );
  }

  if (error && !questionData) {
    return (
      <div className="max-w-3xl mx-auto py-12 px-4">
        <div className="glass-card p-8 border-red-500/30 text-center space-y-4">
          <AlertCircle className="w-10 h-10 text-red-400 mx-auto" />
          <h2 className="text-lg font-bold text-white">Unable to Generate Question</h2>
          <p className="text-sm text-red-300">{error}</p>
          <div className="flex justify-center gap-4 pt-2">
            <button
              onClick={fetchQuestion}
              className="px-5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold"
            >
              Retry
            </button>
            <button
              onClick={onBackToDashboard}
              className="px-5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-sm font-semibold"
            >
              Back to Dashboard
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto py-8 px-4 sm:px-6 space-y-6">
      
      {/* Back button & Header */}
      <div className="flex items-center justify-between">
        <button
          onClick={onBackToDashboard}
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-400 hover:text-white transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Dashboard</span>
        </button>

        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-slate-800 border border-slate-700 text-slate-300">
            Skill: <strong className="text-white">{questionData?.skill}</strong>
          </span>
          <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400">
            Topic: <strong className="text-indigo-300">{questionData?.topic}</strong>
          </span>
          <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-purple-500/10 border border-purple-500/20 text-purple-300">
            {questionData?.difficulty}
          </span>
        </div>
      </div>

      {/* Adaptive Context Banner */}
      {questionData?.recommendation_context && (
        <div className="p-3.5 rounded-xl bg-indigo-950/40 border border-indigo-500/20 text-xs text-indigo-300 flex items-start gap-2.5">
          <Sparkles className="w-4 h-4 text-indigo-400 shrink-0 mt-0.5" />
          <div>
            <strong className="text-white">Adaptive Focus: </strong>
            {questionData.recommendation_context.reason}
          </div>
        </div>
      )}

      {/* Question Card */}
      <div className="glass-card p-6 sm:p-8 space-y-4 border-indigo-500/30">
        <div className="flex items-center gap-2 text-indigo-400 text-xs font-bold uppercase tracking-wider">
          <Code2 className="w-4 h-4" />
          <span>Interview Question</span>
        </div>

        <h2 className="text-lg sm:text-xl font-bold text-white leading-snug">
          {questionData?.question}
        </h2>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-300 text-sm">
          {error}
        </div>
      )}

      {/* Answer Form */}
      <form onSubmit={handleEvaluate} className="space-y-4">
        <div className="glass-card p-4 sm:p-6 space-y-2">
          <div className="flex items-center justify-between mb-1">
            <label className="text-xs font-semibold uppercase tracking-wider text-slate-400">
              Your Technical Answer
            </label>
            <span className="text-[11px] text-slate-500">
              Tip: Explain core concepts, edge cases, and code structure. (Press Ctrl+Enter to submit)
            </span>
          </div>

          <textarea
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            onKeyDown={handleKeyDown}
            rows={8}
            placeholder="Write your explanation or code query here..."
            className="w-full bg-slate-950/90 border border-slate-800 rounded-xl p-4 text-sm text-white placeholder:text-slate-600 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 font-mono text-xs leading-relaxed"
            required
            autoFocus
          />

          <div className="flex items-center justify-between pt-2">
            <span className="text-[11px] text-slate-500">
              {answer.trim().split(/\s+/).filter(Boolean).length} words
            </span>

            <button
              type="submit"
              disabled={evaluating || !answer.trim()}
              className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-indigo-700 hover:from-indigo-500 hover:to-indigo-600 text-white font-semibold text-sm shadow-lg shadow-indigo-600/30 flex items-center gap-2 transition-all disabled:opacity-50 cursor-pointer"
            >
              {evaluating ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin text-white" />
                  <span>Evaluating Answer with Qwen3...</span>
                </>
              ) : (
                <>
                  <span>Evaluate Answer</span>
                  <Send className="w-4 h-4" />
                </>
              )}
            </button>
          </div>
        </div>
      </form>

    </div>
  );
}
