import React from 'react';

export default function ReadinessGauge({ readiness = 0 }) {
  // SVG circular arc parameters
  const radius = 56;
  const strokeWidth = 10;
  const normalizedRadius = radius - strokeWidth / 2;
  const circumference = normalizedRadius * 2 * Math.PI;
  const strokeDashoffset = circumference - (readiness / 100) * circumference;

  let colorClass = "text-red-500 stroke-current";
  let bgGlow = "shadow-red-500/10";
  let statusText = "Needs Remediation";

  if (readiness >= 75) {
    colorClass = "text-emerald-400 stroke-current";
    bgGlow = "shadow-emerald-500/20";
    statusText = "Strong Candidate";
  } else if (readiness >= 50) {
    colorClass = "text-amber-400 stroke-current";
    bgGlow = "shadow-amber-500/20";
    statusText = "Moderate Readiness";
  }

  return (
    <div className={`glass-card p-6 flex items-center gap-6 ${bgGlow}`}>
      <div className="relative w-32 h-32 flex items-center justify-center shrink-0">
        <svg height={radius * 2} width={radius * 2} className="rotate-[-90deg]">
          {/* Background track circle */}
          <circle
            stroke="#1e293b"
            fill="transparent"
            strokeWidth={strokeWidth}
            r={normalizedRadius}
            cx={radius}
            cy={radius}
          />
          {/* Progress circle */}
          <circle
            className={`${colorClass} transition-all duration-1000 ease-out`}
            fill="transparent"
            strokeWidth={strokeWidth}
            strokeDasharray={`${circumference} ${circumference}`}
            style={{ strokeDashoffset }}
            strokeLinecap="round"
            r={normalizedRadius}
            cx={radius}
            cy={radius}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-3xl font-extrabold tracking-tight text-white">{readiness}%</span>
          <span className="text-[10px] uppercase font-semibold text-slate-400 tracking-wider">Readiness</span>
        </div>
      </div>

      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1.5">
          <h3 className="text-lg font-bold text-white tracking-tight">Job Readiness Score</h3>
          <span className={`text-[11px] font-semibold px-2 py-0.5 rounded-full border ${
            readiness >= 75 
              ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' 
              : readiness >= 50 
                ? 'bg-amber-500/10 text-amber-400 border-amber-500/20'
                : 'bg-red-500/10 text-red-400 border-red-500/20'
          }`}>
            {statusText}
          </span>
        </div>
        <p className="text-xs text-slate-400 leading-relaxed">
          Deterministic calculation based on weighted coverage of required (70%) and preferred (30%) job competencies.
        </p>
      </div>
    </div>
  );
}
