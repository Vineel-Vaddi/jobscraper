import React, { useState, useEffect } from 'react';

export default function ResumeHistoryPage() {
  const [variants, setVariants] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('http://localhost:8000/api/resume-variants/history', { credentials: 'include' })
      .then(r => r.json()).then(setVariants)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="p-8">Loading history...</div>;

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-5xl mx-auto">
        <header className="mb-8">
          <h1 className="text-2xl font-bold text-gray-900">Resume History</h1>
          <p className="text-gray-500 text-sm mt-1">All your tailored resume variants in one place.</p>
        </header>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <table className="w-full text-left">
            <thead className="bg-gray-50 text-xs uppercase text-gray-500 border-b">
              <tr>
                <th className="p-4 font-bold">Job Title</th>
                <th className="p-4 font-bold">Company</th>
                <th className="p-4 font-bold">Status</th>
                <th className="p-4 font-bold">ATS</th>
                <th className="p-4 font-bold">Validator</th>
                <th className="p-4 font-bold">Applied</th>
                <th className="p-4 font-bold">Date</th>
                <th className="p-4 font-bold">Actions</th>
              </tr>
            </thead>
            <tbody className="text-sm">
              {variants.map(v => (
                <tr key={v.id} className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="p-4 font-medium text-gray-900">{v.job_title}</td>
                  <td className="p-4 text-gray-600">{v.company}</td>
                  <td className="p-4">
                    <span className={`px-2 py-1 rounded text-xs font-bold ${
                      v.status === 'success' ? 'bg-green-100 text-green-800' :
                      v.status === 'failed' ? 'bg-red-100 text-red-800' :
                      'bg-yellow-100 text-yellow-800'
                    }`}>{v.status}</span>
                  </td>
                  <td className="p-4 text-gray-600">{v.ats_coverage != null ? `${v.ats_coverage}%` : '-'}</td>
                  <td className="p-4">
                    {v.validator_status === 'pass'
                      ? <span className="text-green-600 font-bold text-xs">PASS</span>
                      : v.validator_status
                        ? <span className="text-red-600 font-bold text-xs">REVIEW</span>
                        : '-'}
                  </td>
                  <td className="p-4">{v.applied ? '✓ Applied' : '—'}</td>
                  <td className="p-4 text-gray-500 text-xs">{new Date(v.created_at).toLocaleDateString()}</td>
                  <td className="p-4 flex gap-2">
                    <a href={`/dashboard/tailor/${v.id}`} className="text-blue-600 hover:underline text-xs font-medium">Review</a>
                    {v.has_docx && <a href={`http://localhost:8000/api/resume-variants/${v.id}/download/docx`} className="text-gray-500 hover:underline text-xs">DOCX</a>}
                    {v.has_pdf && <a href={`http://localhost:8000/api/resume-variants/${v.id}/download/pdf`} className="text-gray-500 hover:underline text-xs">PDF</a>}
                  </td>
                </tr>
              ))}
              {variants.length === 0 && (
                <tr><td colSpan={8} className="p-12 text-center text-gray-400">No tailored resumes yet.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
