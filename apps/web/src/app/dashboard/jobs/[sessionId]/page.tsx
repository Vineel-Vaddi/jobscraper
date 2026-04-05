'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function RankedJobsPage({ params }: { params: { sessionId: string } }) {
  const [session, setSession] = useState<any>(null);
  const [jobs, setJobs] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const router = useRouter();
  
  const sessionId = params.sessionId;

  const fetchData = async () => {
    try {
      const sessResp = await fetch(`http://localhost:8000/api/jobs/sessions/${sessionId}`, { credentials: 'include' });
      if (sessResp.ok) {
        setSession(await sessResp.json());
      }
      
      const jobsResp = await fetch(`http://localhost:8000/api/jobs/sessions/${sessionId}/jobs`, { credentials: 'include' });
      if (jobsResp.ok) {
        setJobs(await jobsResp.json());
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(() => {
      setSession((curr: any) => {
        if (!curr || ['pending', 'processing'].includes(curr.status)) {
          fetchData();
        }
        return curr;
      });
    }, 3000);
    return () => clearInterval(interval);
  }, [sessionId]);

  if (loading && !session) return <div className="p-8">Loading...</div>;
  if (!session) return <div className="p-8">Session not found.</div>;

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-5xl mx-auto">
        <header className="mb-8 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 tracking-tight">Ranked Jobs</h1>
            <p className="text-gray-500 mt-1 max-w-xl truncate text-sm">{session.source_url}</p>
          </div>
          <a href="/dashboard/jobs" className="text-blue-600 hover:text-blue-800">Back to Intake</a>
        </header>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-8 flex gap-6 text-sm">
          <div>Status: <strong className="uppercase">{session.status}</strong></div>
          <div>Raw Jobs: <strong>{session.raw_result_count}</strong></div>
          <div>Normalized: <strong>{session.normalized_result_count}</strong></div>
          <div>Deduped: <strong>{session.deduped_result_count}</strong></div>
        </div>

        {session.status === 'failed' && (
          <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-8 text-red-700">
            <strong>Error ({session.ingest_error_code}):</strong> {session.ingest_error_message}
          </div>
        )}

        <div className="flex flex-col gap-4">
          {jobs.length === 0 && session.status === 'success' && (
            <p className="text-gray-500">No jobs found or processed.</p>
          )}
          
          {jobs.map(job => (
            <div key={job.id} onClick={() => router.push(`/dashboard/jobs/${sessionId}/${job.id}`)} className="bg-white rounded-lg shadow-sm border border-gray-200 p-5 cursor-pointer hover:shadow-md transition">
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="text-xl font-bold text-gray-900">{job.title}</h3>
                  <p className="text-gray-600 text-sm mt-1">{job.company} • {job.location || 'Remote'} • {job.work_mode}</p>
                  
                  {job.fit_reasons_json && (
                    <div className="mt-3 flex flex-wrap gap-2">
                       {JSON.parse(job.fit_reasons_json).slice(0, 2).map((reason: string, i: number) => (
                         <span key={i} className="px-2 py-1 bg-green-50 text-green-700 rounded text-xs font-medium border border-green-100">✓ {reason}</span>
                       ))}
                    </div>
                  )}
                </div>
                <div className="text-right">
                   <div className="text-3xl font-bold text-blue-600">{job.fit_score || 0}</div>
                   <div className="text-xs text-gray-500 mt-1 uppercase tracking-wider font-semibold">Fit Score</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
