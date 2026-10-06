import React from 'react';
import { CheckCircle2, AlertTriangle, XCircle, ArrowRight, RotateCw, Sparkles, TrendingUp, HelpCircle } from 'lucide-react';

export default function ResultPage({ evaluationData, onNextQuestion, onBackToDashboard }) {
  const {
    skill,
    topic,
    question,
    answer,
    score,
    correctness,
    missing_concepts = [],
    feedback,
    previous_skill_score = 0,
    new_skill_score = 0,
    recommended_next_topic,
    next_recommendation,
  } = evaluationData;

  const isScoreGain = new_skill_score >= previous_skill_score;
  const scoreDiff = new_skill_score - previous_skill_score;

  let correctnessBadge = (
    <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
      <CheckCircle2 className="w-3.5 h-3.5" />
      Correct
    </span>
  );

  if (correctness === 'Partially Correct' || (score >= 40 && score < 80)) {
    correctnessBadge = (
      <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-amber-500/10 text-amber-400 border border-amber-500/20">
        <AlertTriangle className="w-3.5 h-3.5" />
        Partially Correct
      </span>
    );
  } else if (correctness === 'Incorrect' || score < 40) {
    correctnessBadge = (
      <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-rose-500/10 text-rose-400 border border-rose-500/20">
        <XCircle className="w-3.5 h-3.5" />
        Incorrect
      </span>
    );
  }

  return (
    <div className="max-w-4xl mx-auto py-8 px-4 sm:px-6 space-y-8">
      
      {/* Top Banner: Score & Correctness */}
      <div className="glass-card p-6 sm:p-8 bg-gradient-to-r from-slate-900 via-slate-900/90 to-indigo-950/40 border-indigo-500/30">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-6">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="text-xs font-semibold text-slate-400">Skill: {skill}</span>
              <span className="text-slate-600">•</span>
              <span className="text-xs text-indigo-300">Topic: {topic}</span>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-4xl sm:text-5xl font-black text-white tracking-tight">
                {score} <span className="text-2xl text-slate-500 font-normal">/ 100</span>
              </div>
              {correctnessBadge}
            </div>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={onNextQuestion}
              className="px-6 py-3 rounded-xl bg-gradient-to-r from-indigo-600 to-indigo-700 hover:from-indigo-500 hover:to-indigo-600 text-white font-semibold text-sm shadow-lg shadow-indigo-600/30 flex items-center gap-2 transition-all active:scale-95"
            >
              <span>Practice Next</span>
              <ArrowRight className="w-4 h-4" />
            </button>
            <button
              onClick={onBackToDashboard}
              className="px-4 py-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-sm font-semibold transition-colors"
            >
              Dashboard
            </button>
          </div>
        </div>
      </div>

      {/* Row: Skill Update Formula Card & Next Adaptive Topic */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
        
        {/* Skill Score Update (Before -> After) */}
        <div className="glass-card p-6 border-indigo-500/20">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold uppercase tracking-wider text-indigo-400 flex items-center gap-1.5">
              <TrendingUp className="w-4 h-4" />
              Skill State Update
            </span>
            <span className="text-[11px] font-mono text-slate-400">
              0.7×prev + 0.3×ans
            </span>
          </div>

          <div className="flex items-center gap-4 my-2">
            <div className="text-center p-3 rounded-xl bg-slate-950/80 border border-slate-800 flex-1">
              <span className="text-[10px] text-slate-500 uppercase block font-semibold">Previous</span>
              <span className="text-2xl font-bold text-slate-300">{previous_skill_score}%</span>
            </div>

            <ArrowRight className="w-5 h-5 text-indigo-400 shrink-0" />

            <div className="text-center p-3 rounded-xl bg-slate-950/80 border border-indigo-500/30 flex-1">
              <span className="text-[10px] text-indigo-400 uppercase block font-semibold">Updated</span>
              <span className="text-2xl font-extrabold text-white">{new_skill_score}%</span>
            </div>
          </div>

          <p className="text-xs text-slate-400 mt-3 leading-relaxed">
            {skill}: {isScoreGain ? `Proficiency increased by +${scoreDiff}%` : `Score adjusted by ${scoreDiff}%`} based on evaluation.
          </p>
        </div>

        {/* Next Recommendation from Adaptive Planner */}
        <div className="glass-card p-6 border-purple-500/20 bg-gradient-to-br from-purple-950/20 to-slate-900">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold uppercase tracking-wider text-purple-400 flex items-center gap-1.5">
              <Sparkles className="w-4 h-4" />
              Next Adaptive Step
            </span>
            {next_recommendation?.difficulty && (
              <span className="text-[11px] font-semibold px-2 py-0.5 rounded-full bg-purple-500/10 text-purple-300 border border-purple-500/20">
                {next_recommendation.difficulty}
              </span>
            )}
          </div>

          <h3 className="text-base font-bold text-white mb-1.5">
            {next_recommendation?.recommended_topic || recommended_next_topic}
          </h3>

          <p className="text-xs text-slate-300 leading-relaxed mb-3">
            {next_recommendation?.reason || 'Calculated by adaptive planner to close remaining gap.'}
          </p>

          <button
            onClick={onNextQuestion}
            className="text-xs font-semibold text-purple-400 hover:text-purple-300 flex items-center gap-1 group"
          >
            <span>Launch this question now</span>
            <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
          </button>
        </div>

      </div>

      {/* Evaluator Technical Feedback */}
      <div className="glass-card p-6 space-y-4">
        <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300">
          AI Interviewer Feedback
        </h3>
        <div className="p-4 rounded-xl bg-slate-950/70 border border-slate-800 text-sm text-slate-200 leading-relaxed">
          {feedback}
        </div>
      </div>

      {/* Missing Concepts Breakdown */}
      {missing_concepts && missing_concepts.length > 0 && (
        <div className="glass-card p-6 space-y-3">
          <h3 className="text-sm font-bold uppercase tracking-wider text-amber-400 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4" />
            Concepts Missed / Suggested Enhancements
          </h3>
          <ul className="space-y-2">
            {missing_concepts.map((concept, idx) => (
              <li key={idx} className="p-3 rounded-xl bg-amber-500/5 border border-amber-500/20 text-xs text-amber-200 flex items-start gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-amber-400 shrink-0 mt-1.5" />
                <span>{concept}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Question & Submitted Answer Review */}
      <div className="glass-card p-6 space-y-4 text-xs">
        <div>
          <span className="font-bold text-slate-400 uppercase tracking-wider block mb-1">Question</span>
          <p className="text-slate-200">{question}</p>
        </div>

        <div className="pt-3 border-t border-slate-800">
          <span className="font-bold text-slate-400 uppercase tracking-wider block mb-1">Your Submitted Answer</span>
          <pre className="p-3 rounded-lg bg-slate-950 border border-slate-800 font-mono text-[11px] text-slate-300 whitespace-pre-wrap">
            {answer}
          </pre>
        </div>
      </div>

    </div>
  );
}
