import React from 'react';
import { Play, Sparkles, CheckCircle2, AlertCircle, ArrowRight, Layers, Award } from 'lucide-react';
import ReadinessGauge from '../components/ReadinessGauge';
import SkillBadge from '../components/SkillBadge';

export default function DashboardPage({ analysisData, onStartPractice, onRefreshProgress }) {
  const {
    candidate_name,
    target_role,
    readiness = 0,
    extracted_skills = [],
    projects = [],
    skill_gaps = [],
    matched_skills = [],
    recommended_focus = null,
  } = analysisData;

  // Classify skills
  const strongGaps = skill_gaps.filter(g => g.score >= 50);
  const criticalGaps = skill_gaps.filter(g => g.score < 50);

  return (
    <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8 space-y-8">
      
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 glass-card p-6 border-indigo-500/20 bg-gradient-to-r from-slate-900 via-slate-900/90 to-indigo-950/40">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-bold uppercase tracking-wider text-indigo-400">Candidate Profile</span>
            <span className="text-slate-600">•</span>
            <span className="text-xs text-slate-400">Target Role:</span>
            <span className="text-xs font-semibold text-white px-2 py-0.5 rounded-md bg-slate-800 border border-slate-700">
              {target_role}
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            {candidate_name || 'Candidate Dashboard'}
          </h1>
        </div>

        <button
          onClick={onStartPractice}
          className="px-6 py-3 rounded-xl bg-gradient-to-r from-indigo-600 to-indigo-700 hover:from-indigo-500 hover:to-indigo-600 text-white font-semibold text-sm shadow-lg shadow-indigo-600/30 flex items-center justify-center gap-2 shrink-0 transition-transform active:scale-95"
        >
          <Play className="w-4 h-4 fill-white" />
          <span>Start Targeted Practice</span>
        </button>
      </div>

      {/* Row 1: Readiness Gauge & Recommended Practice */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left: Job Readiness Gauge */}
        <div className="lg:col-span-5">
          <ReadinessGauge readiness={readiness} />
        </div>

        {/* Right: Recommended Practice Next (Adaptive Planner Card) */}
        <div className="lg:col-span-7 glass-card p-6 border-indigo-500/30 relative overflow-hidden bg-gradient-to-br from-indigo-950/30 via-slate-900 to-slate-900">
          <div className="absolute top-0 right-0 p-6 opacity-10 pointer-events-none">
            <Sparkles className="w-32 h-32 text-indigo-400" />
          </div>

          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2 text-indigo-400 text-xs font-bold uppercase tracking-wider">
              <Sparkles className="w-4 h-4" />
              <span>Adaptive Planner Recommendation</span>
            </div>
            {recommended_focus?.difficulty && (
              <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                {recommended_focus.difficulty} Level
              </span>
            )}
          </div>

          <h2 className="text-xl font-bold text-white mb-2">
            Practice Next: <span className="text-indigo-400">{recommended_focus?.recommended_topic || 'Targeted Practice'}</span>
          </h2>

          <p className="text-sm text-slate-300 mb-4 leading-relaxed">
            {recommended_focus?.reason || 'Based on your resume and target role requirements.'}
          </p>

          <div className="flex items-center justify-between pt-4 border-t border-slate-800">
            <div className="text-xs text-slate-400">
              Weakness Focus: <span className="text-white font-medium">{recommended_focus?.current_weakness || 'General'}</span>
            </div>

            <button
              onClick={onStartPractice}
              className="inline-flex items-center gap-1.5 text-xs font-bold text-indigo-400 hover:text-indigo-300 group"
            >
              <span>Launch Question</span>
              <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
            </button>
          </div>
        </div>

      </div>

      {/* Row 2: Skill Gaps vs Demonstrated Strengths */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Skill Gaps Card */}
        <div className="lg:col-span-7 glass-card p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <AlertCircle className="w-5 h-5 text-amber-400" />
              <h3 className="text-base font-bold text-white">Identified Skill Gaps ({skill_gaps.length})</h3>
            </div>
            <span className="text-xs text-slate-400">Ranked by Priority & Need</span>
          </div>

          {skill_gaps.length === 0 ? (
            <div className="p-6 text-center text-slate-400 text-sm">
              No critical skill gaps found! All required skills are strongly demonstrated.
            </div>
          ) : (
            <div className="space-y-2.5">
              {skill_gaps.map((gap, idx) => (
                <SkillBadge
                  key={idx}
                  skill={{ skill_name: gap.skill_name, score: gap.score, source: 'job_required' }}
                  showPriority={true}
                  priority={gap.priority}
                  importance={gap.importance}
                />
              ))}
            </div>
          )}
        </div>

        {/* Demonstrated Skills & Projects */}
        <div className="lg:col-span-5 space-y-6">
          
          {/* Demonstrated Skills */}
          <div className="glass-card p-6">
            <div className="flex items-center gap-2 mb-4">
              <Award className="w-5 h-5 text-emerald-400" />
              <h3 className="text-base font-bold text-white">Candidate Skills ({extracted_skills.length})</h3>
            </div>
            <div className="flex flex-wrap gap-2">
              {extracted_skills.map((skill, idx) => (
                <span
                  key={idx}
                  className="text-xs font-semibold px-3 py-1.5 rounded-lg bg-slate-800/80 border border-slate-700/80 text-slate-200"
                >
                  {skill}
                </span>
              ))}
            </div>
          </div>

          {/* Technical Projects */}
          {projects.length > 0 && (
            <div className="glass-card p-6">
              <div className="flex items-center gap-2 mb-4">
                <Layers className="w-5 h-5 text-indigo-400" />
                <h3 className="text-base font-bold text-white">Extracted Projects ({projects.length})</h3>
              </div>
              <ul className="space-y-2 text-xs text-slate-300">
                {projects.map((proj, idx) => (
                  <li key={idx} className="p-2.5 rounded-lg bg-slate-950/60 border border-slate-800 leading-relaxed">
                    {proj}
                  </li>
                ))}
              </ul>
            </div>
          )}

        </div>

      </div>

    </div>
  );
}
