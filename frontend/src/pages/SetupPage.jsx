import React, { useState } from 'react';
import { FileUp, Target, Briefcase, ArrowRight, Loader2, Sparkles, CheckCircle, FileText } from 'lucide-react';
import { analyzeProfile } from '../services/api';

export default function SetupPage({ onAnalysisComplete }) {
  const [resumeFile, setResumeFile] = useState(null);
  const [targetRole, setTargetRole] = useState('AI Engineer');
  const [jobDescription, setJobDescription] = useState(
`We are seeking an AI Engineer to build scalable machine learning systems and intelligent agent workflows.
Requirements:
- Strong proficiency in Python and REST APIs (FastAPI preferred).
- Deep experience with SQL databases and complex query design (JOINs, aggregation).
- Familiarity with Machine Learning fundamentals and model evaluation.
Preferred:
- Experience with Docker containerization.
- Knowledge of local LLM orchestration and Ollama.`
  );
  const [loading, setLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState('');
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      if (!file.name.toLowerCase().endsWith('.pdf')) {
        setError('Please select a valid PDF file.');
        return;
      }
      setResumeFile(file);
      setError(null);
    }
  };

  const handleUseSampleResume = async () => {
    try {
      // Create a sample synthetic PDF in memory for fast testing
      // using standard PDF generation or placeholder text
      setLoading(true);
      setLoadingStep('Generating sample candidate PDF...');
      
      // We can generate a client-side minimal PDF Blob or submit test formData
      const samplePdfContent = "%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<<>>/Contents 4 0 R>>endobj\n4 0 obj<</Length 240>>stream\nBT\n/F1 12 Tf\n50 720 Td\n(Alex Chen - Software & AI Engineer) Tj\n0 -20 Td\n(Skills: Python, FastAPI, React, JavaScript, Git) Tj\n0 -20 Td\n(Projects: Built Realtime Data Pipeline with FastAPI and Redis.) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000056 00000 n \n0000000111 00000 n \n0000000212 00000 n \ntrailer<</Size 5/Root 1 0 R>>\nstartxref\n504\n%%EOF";
      const blob = new Blob([samplePdfContent], { type: 'application/pdf' });
      const sampleFile = new File([blob], "Alex_Chen_Resume.pdf", { type: "application/pdf" });
      setResumeFile(sampleFile);
      setLoading(false);
      setLoadingStep('');
    } catch (err) {
      setLoading(false);
      setError('Failed to create sample resume: ' + err.message);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!resumeFile) {
      setError('Please upload a PDF resume or click "Use Sample Resume".');
      return;
    }
    if (!targetRole.trim()) {
      setError('Please provide a target role.');
      return;
    }
    if (!jobDescription.trim()) {
      setError('Please provide a job description.');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      setLoadingStep('Extracting resume text with PyMuPDF...');
      
      const formData = new FormData();
      formData.append('resume', resumeFile);
      formData.append('target_role', targetRole);
      formData.append('job_description', jobDescription);

      setTimeout(() => {
        setLoadingStep('Analyzing skills & job requirements with Qwen3:4b...');
      }, 1500);

      const result = await analyzeProfile(formData);
      onAnalysisComplete(result);
    } catch (err) {
      setError(err.message || 'Failed to analyze profile.');
    } finally {
      setLoading(false);
      setLoadingStep('');
    }
  };

  return (
    <div className="max-w-4xl mx-auto py-10 px-4 sm:px-6">
      
      {/* Hero */}
      <div className="text-center mb-10">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-semibold uppercase tracking-wider mb-4">
          <Sparkles className="w-3.5 h-3.5" />
          Adaptive Learning Loop
        </div>
        <h1 className="text-4xl sm:text-5xl font-extrabold tracking-tight text-white mb-4">
          Prepare for your dream role with <span className="bg-gradient-to-r from-indigo-400 via-indigo-300 to-purple-400 bg-clip-text text-transparent">Precision</span>
        </h1>
        <p className="text-slate-400 text-base sm:text-lg max-w-2xl mx-auto">
          Upload your resume and target job description. PLACEWISE identifies your specific skill gaps and adapts practice questions in real time.
        </p>
      </div>

      {error && (
        <div className="mb-6 p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-300 text-sm flex items-start gap-3">
          <span className="font-bold">Error:</span> {error}
        </div>
      )}

      {/* Main Setup Form */}
      <form onSubmit={handleSubmit} className="space-y-6">
        
        {/* Step 1: Resume Upload */}
        <div className="glass-card p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-lg bg-indigo-500/20 text-indigo-400 flex items-center justify-center font-bold text-sm">
                1
              </div>
              <div>
                <h3 className="text-base font-bold text-white">Upload Candidate Resume (PDF)</h3>
                <p className="text-xs text-slate-400">Extracted locally using PyMuPDF. Data never leaves your machine.</p>
              </div>
            </div>
            
            <button
              type="button"
              onClick={handleUseSampleResume}
              className="text-xs font-medium text-indigo-400 hover:text-indigo-300 underline underline-offset-2 flex items-center gap-1"
            >
              <FileText className="w-3.5 h-3.5" />
              Load Sample Resume
            </button>
          </div>

          <div className="relative border-2 border-dashed border-slate-700 hover:border-indigo-500/60 rounded-xl p-6 text-center transition-colors bg-slate-950/40">
            <input
              type="file"
              accept=".pdf"
              onChange={handleFileChange}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            />
            {resumeFile ? (
              <div className="flex items-center justify-center gap-3 text-indigo-300">
                <CheckCircle className="w-6 h-6 text-emerald-400" />
                <span className="font-semibold text-sm">{resumeFile.name}</span>
                <span className="text-xs text-slate-500">({(resumeFile.size / 1024).toFixed(1)} KB)</span>
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center gap-2">
                <FileUp className="w-8 h-8 text-slate-400" />
                <p className="text-sm font-medium text-slate-300">
                  Drag and drop your PDF resume here, or <span className="text-indigo-400 underline">browse</span>
                </p>
                <p className="text-xs text-slate-500">Supports PDF format</p>
              </div>
            )}
          </div>
        </div>

        {/* Step 2: Target Role & Job Description */}
        <div className="glass-card p-6 space-y-4">
          <div className="flex items-center gap-2.5 mb-2">
            <div className="w-8 h-8 rounded-lg bg-indigo-500/20 text-indigo-400 flex items-center justify-center font-bold text-sm">
              2
            </div>
            <div>
              <h3 className="text-base font-bold text-white">Target Role & Job Description</h3>
              <p className="text-xs text-slate-400">Specifies the role and technical requirements for gap calculation.</p>
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1.5">
              Target Role
            </label>
            <div className="relative">
              <Target className="w-4 h-4 text-slate-500 absolute left-3.5 top-3.5" />
              <input
                type="text"
                value={targetRole}
                onChange={(e) => setTargetRole(e.target.value)}
                placeholder="e.g. AI Engineer, Full Stack Developer, Backend Specialist"
                className="w-full bg-slate-950/80 border border-slate-800 rounded-xl pl-10 pr-4 py-2.5 text-sm text-white placeholder:text-slate-600 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
                required
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1.5">
              Job Description
            </label>
            <div className="relative">
              <Briefcase className="w-4 h-4 text-slate-500 absolute left-3.5 top-3.5" />
              <textarea
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
                rows={6}
                placeholder="Paste the target job description requirements here..."
                className="w-full bg-slate-950/80 border border-slate-800 rounded-xl pl-10 pr-4 py-2.5 text-sm text-white placeholder:text-slate-600 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 font-mono text-xs leading-relaxed"
                required
              />
            </div>
          </div>
        </div>

        {/* Submit Action */}
        <div className="flex justify-end">
          <button
            type="submit"
            disabled={loading}
            className="w-full sm:w-auto px-8 py-3.5 rounded-xl bg-gradient-to-r from-indigo-600 to-indigo-700 hover:from-indigo-500 hover:to-indigo-600 text-white font-semibold text-sm shadow-lg shadow-indigo-600/30 flex items-center justify-center gap-2.5 transition-all disabled:opacity-50 cursor-pointer"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin text-white" />
                <span>{loadingStep || 'Analyzing Profile with Qwen3...'}</span>
              </>
            ) : (
              <>
                <span>Analyze My Profile</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </div>

      </form>
    </div>
  );
}
