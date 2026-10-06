import React from 'react';
import { CheckCircle2, AlertTriangle, AlertCircle, Bookmark } from 'lucide-react';

export default function SkillBadge({ skill, showPriority = false, priority = null, importance = null }) {
  const score = skill?.score ?? 0;
  const isStrong = score >= 70;
  const isModerate = score >= 50 && score < 70;

  return (
    <div className="flex items-center justify-between p-3.5 rounded-xl bg-slate-900/60 border border-slate-800/80 hover:border-slate-700 transition-colors">
      <div className="flex items-center gap-2.5 min-w-0">
        {isStrong ? (
          <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
        ) : isModerate ? (
          <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0" />
        ) : (
          <AlertCircle className="w-4 h-4 text-red-400 shrink-0" />
        )}
        
        <div className="truncate">
          <div className="flex items-center gap-1.5">
            <span className="text-sm font-semibold text-slate-100 truncate">{skill.skill_name}</span>
            {importance && (
              <span className={`text-[9px] uppercase font-bold px-1.5 py-0.2 rounded border ${
                importance === 'required' 
                  ? 'bg-rose-500/10 text-rose-400 border-rose-500/20' 
                  : 'bg-blue-500/10 text-blue-400 border-blue-500/20'
              }`}>
                {importance}
              </span>
            )}
          </div>
          {skill.source && (
            <span className="text-[10px] text-slate-500 block">
              Source: {skill.source === 'job_required' ? 'JD Requirement' : skill.source === 'job_preferred' ? 'JD Preferred' : 'Candidate Resume'}
            </span>
          )}
        </div>
      </div>

      <div className="flex items-center gap-3 shrink-0">
        {showPriority && priority && (
          <span className="text-[11px] font-semibold px-2 py-0.5 rounded-md bg-amber-500/10 text-amber-300 border border-amber-500/20">
            Priority {priority}
          </span>
        )}
        <div className="text-right">
          <span className={`text-sm font-bold ${
            isStrong ? 'text-emerald-400' : isModerate ? 'text-amber-400' : 'text-red-400'
          }`}>
            {score}%
          </span>
        </div>
      </div>
    </div>
  );
}
