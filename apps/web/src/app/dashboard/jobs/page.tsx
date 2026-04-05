'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function JobsIntakePage() {
  const [url, setUrl] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [sessions, setSessions] = useState<any[]>([]);
  const router = useRouter();

  const fetchSessions = async () => {
    try {
      const resp = await fetch('http://localhost:8000/api/jobs/sessions', { credentials: 'include' });
      if (resp.ok) {
        setSessions(await resp.json());
      }
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchSessions();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const resp = await fetch('http://localhost:8000/api/jobs/intake', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ source_url: url })
      });
      if (resp.ok) {
        const session = await resp.json();
        router.push(`/dashboard/jobs/${session.id}`);
      } else {
        setError("Failed to create job intake session.");
      }
    } catch {
      setError("Network error occurred.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <header className="mb-8 flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-900 tracking-tight">Job Search Intake</h1>
          <a href="/dashboard" className="text-blue-600 hover:text-blue-800">Back to Dashboard</a>
        </header>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8 mb-8">
          <h2 className="text-xl font-semibold mb-4 text-gray-800">Paste Job Search URL</h2>
          <form onSubmit={handleSubmit} className="flex gap-4">
            <input 
              type="url" 
              required
              placeholder="https://linkedin.com/jobs/search?keywords=Software%20Engineer" 
              className="flex-1 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-gray-900"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              disabled={loading}
            />
            <button 
              type="submit" 
              disabled={loading}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? 'Processing...' : 'Ingest Jobs'}
            </button>
          </form>
          {error && <p className="text-red-500 mt-2">{error}</p>}
        </div>

        <div>
          <h3 className="text-xl font-semibold text-gray-800 mb-4">Past Sessions</h3>
          {sessions.length === 0 ? (
            <p className="text-gray-500">No past sessions found.</p>
          ) : (
            <div className="flex flex-col gap-3">
              {sessions.map(s => (
                <div key={s.id} className="bg-white p-4 rounded-lg shadow-sm border border-gray-200 flex justify-between items-center">
                  <div>
                    <p className="font-medium text-gray-900 text-sm truncate max-w-lg">{s.source_url}</p>
                    <p className="text-sm text-gray-500">
                      Status: <span className="font-semibold text-gray-700">{s.status}</span> • 
                      Deduped: {s.deduped_result_count} • 
                      {new Date(s.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <a href={`/dashboard/jobs/${s.id}`} className="text-blue-600 font-medium hover:underline">View Jobs</a>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
