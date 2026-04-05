'use client';

import React, { useState, useEffect } from 'react';

export default function AdminDashboardPage() {
  const [summary, setSummary] = useState<any>(null);
  const [runs, setRuns] = useState<any[]>([]);
  const [health, setHealth] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAdminData = async () => {
      try {
        const [sumResp, runResp, healthResp] = await Promise.all([
          fetch('http://localhost:8000/api/admin/system-summary', { credentials: 'include' }),
          fetch('http://localhost:8000/api/admin/runs?limit=30', { credentials: 'include' }),
          fetch('http://localhost:8000/api/admin/health/deep', { credentials: 'include' })
        ]);
        
        if (sumResp.ok) setSummary(await sumResp.json());
        if (runResp.ok) setRuns(await runResp.json());
        if (healthResp.ok) setHealth(await healthResp.json());
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    fetchAdminData();
  }, []);

  if (loading) return <div className="p-8">Loading Admin Metrics...</div>;

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto space-y-8">
        <header className="flex justify-between items-center bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <div>
            <h1 className="text-3xl font-extrabold text-gray-900">Diagnostics & Observation</h1>
            <p className="text-gray-500 mt-1 text-sm">System Health and Celery Pipeline Runs</p>
          </div>
          <div className="flex items-center gap-4 text-sm font-bold">
             <div className="flex items-center gap-2">
                <span className={`w-3 h-3 rounded-full ${health?.status === 'ok' ? 'bg-green-500' : 'bg-red-500'}`}></span>
                System API
             </div>
             <div className="flex items-center gap-2">
                <span className={`w-3 h-3 rounded-full ${health?.database === 'ok' ? 'bg-green-500' : 'bg-red-500'}`}></span>
                Database 
             </div>
          </div>
        </header>

        {summary && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
             <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                 <div className="text-sm font-bold text-gray-500 uppercase">Jobs Ranked</div>
                 <div className="text-3xl font-extrabold mt-2 text-blue-600">{summary.total_jobs}</div>
             </div>
             <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                 <div className="text-sm font-bold text-gray-500 uppercase">Resumes Tailored</div>
                 <div className="text-3xl font-extrabold mt-2 text-indigo-600">{summary.total_variants}</div>
             </div>
             <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                 <div className="text-sm font-bold text-green-700 uppercase">Successful Runs</div>
                 <div className="text-3xl font-extrabold mt-2 text-green-600">{summary.success_runs}</div>
             </div>
             <div className="bg-white p-6 rounded-xl shadow-sm border border-red-200">
                 <div className="text-sm font-bold text-red-700 uppercase">Failed Runs</div>
                 <div className="text-3xl font-extrabold mt-2 text-red-600">{summary.failed_runs}</div>
             </div>
          </div>
        )}

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <div className="p-6 border-b border-gray-200 bg-gray-50 flex justify-between items-center">
             <h2 className="text-lg font-bold">Pipeline Agent Runs</h2>
             <a href="http://localhost:8000/api/admin/metrics" target="_blank" rel="noreferrer" className="text-blue-500 hover:text-blue-700 text-sm font-bold flex items-center gap-1">
                 View Raw Prometheus Metrics ↗
             </a>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-gray-50 text-xs uppercase text-gray-500 border-b border-gray-200">
                  <th className="p-4 font-bold">Status</th>
                  <th className="p-4 font-bold">Run Type</th>
                  <th className="p-4 font-bold">Duration (ms)</th>
                  <th className="p-4 font-bold">Entity</th>
                  <th className="p-4 font-bold">Start Time</th>
                  <th className="p-4 font-bold">Error Output</th>
                </tr>
              </thead>
              <tbody className="text-sm text-gray-800">
                {runs.map((r, i) => (
                  <tr key={i} className="border-b border-gray-100 hover:bg-gray-50 transition">
                    <td className="p-4">
                       <span className={`px-2 py-1 rounded text-xs font-bold ${
                         r.status === 'success' ? 'bg-green-100 text-green-800' :
                         r.status === 'failed' ? 'bg-red-100 text-red-800' :
                         'bg-yellow-100 text-yellow-800'
                       }`}>
                         {r.status.toUpperCase()}
                       </span>
                    </td>
                    <td className="p-4 font-medium text-gray-900">{r.run_type}</td>
                    <td className="p-4 text-gray-500">{r.duration_ms || '-'}</td>
                    <td className="p-4 text-gray-500 text-xs font-mono">{r.target_entity_type}_{r.target_entity_id}</td>
                    <td className="p-4 text-gray-500">{new Date(r.started_at).toLocaleString()}</td>
                    <td className="p-4 text-xs font-mono text-red-500 max-w-xs truncate" title={r.error_message || r.error_code}>
                       {r.error_code || (r.error_message ? r.error_message.substring(0, 50) + "..." : "-")}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            
            {runs.length === 0 && (
                <div className="p-12 text-center text-gray-500 border-t">No Agent Runs recorded yet.</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
