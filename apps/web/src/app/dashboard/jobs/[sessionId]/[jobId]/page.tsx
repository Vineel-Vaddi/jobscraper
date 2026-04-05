import React, { useState, useEffect } from 'react';

export default function JobDetailPage({ params }: { params: { jobId: string, sessionId: string } }) {
  const [job, setJob] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  
  const jobId = params.jobId;

  useEffect(() => {
    const fetchJob = async () => {
      try {
        const resp = await fetch(`http://localhost:8000/api/jobs/${jobId}`, { credentials: 'include' });
        if (resp.ok) {
          setJob(await resp.json());
        }
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    fetchJob();
  }, [jobId]);

  if (loading) return <div className="p-8">Loading...</div>;
  if (!job) return <div className="p-8 text-red-500">Job not found.</div>;

  const reasons = job.fit_reasons_json ? JSON.parse(job.fit_reasons_json) : [];
  const gaps = job.fit_gaps_json ? JSON.parse(job.fit_gaps_json) : [];
  const requirements = job.requirements_json || {};

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <header className="mb-6 flex justify-between items-center">
          <a href={`/dashboard/jobs/${job.job_search_session_id}`} className="text-blue-600 hover:underline">← Back to Ranked Jobs</a>
          <a href={job.source_job_url} target="_blank" rel="noreferrer" className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700">Apply Externally</a>
        </header>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <div className="p-8 border-b border-gray-200 flex justify-between items-start bg-gray-100/50">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{job.title}</h1>
              <p className="text-lg text-gray-600 mt-2">{job.company}</p>
              <div className="flex gap-4 mt-4 text-sm text-gray-500">
                <span className="flex items-center gap-1">📍 {job.location || 'Unknown'}</span>
                <span className="flex items-center gap-1">🏢 {job.work_mode || 'Unknown'}</span>
                {job.posted_at_raw && <span className="flex items-center gap-1">🕒 {job.posted_at_raw}</span>}
              </div>
            </div>
            <div className="text-center bg-white p-4 rounded-xl shadow-sm border border-gray-100 min-w-32">
              <div className="text-4xl font-extrabold text-blue-600">{job.fit_score || 0}</div>
              <div className="text-xs uppercase text-gray-500 font-bold tracking-wide mt-2">Fit Score</div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3">
            <div className="md:col-span-2 p-8 border-r border-gray-200">
              <h3 className="text-lg font-bold text-gray-900 mb-4">Job Description</h3>
              <div className="prose prose-blue text-sm text-gray-700 max-w-none whitespace-pre-wrap">
                {job.description_text || "No description successfully extracted. This might be a stub from a search list page without rendering the full description."}
              </div>
            </div>
            
            <div className="p-8 bg-gray-50">
              <h3 className="text-base font-bold text-gray-900 mb-4">Suitability Analysis</h3>
              
              {reasons.length > 0 && (
                <div className="mb-6">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-green-700 mb-2">Strengths</h4>
                  <ul className="space-y-2">
                    {reasons.map((r, i) => (
                      <li key={i} className="text-sm text-gray-700 flex items-start gap-2">
                        <span className="text-green-500">✓</span> {r}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {gaps.length > 0 && (
                <div className="mb-6">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-red-700 mb-2">Gaps</h4>
                  <ul className="space-y-2">
                    {gaps.map((g, i) => (
                      <li key={i} className="text-sm text-gray-700 flex items-start gap-2">
                        <span className="text-red-500">!</span> {g}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {requirements.skills && requirements.skills.length > 0 && (
                <div>
                  <h4 className="text-xs font-bold uppercase tracking-wider text-gray-500 mb-2">Extracted Keywords</h4>
                  <div className="flex flex-wrap gap-2">
                    {requirements.skills.map((s, i) => (
                      <span key={i} className="px-2 py-1 bg-gray-200 text-gray-800 rounded text-xs font-medium">{s}</span>
                    ))}
                  </div>
                </div>
              )}

              <div className="mt-8 pt-6 border-t border-gray-200">
                 <button className="w-full bg-gray-900 text-white font-medium py-3 rounded-lg hover:bg-gray-800 transition">
                   Use for Targeting (Phase 4)
                 </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
