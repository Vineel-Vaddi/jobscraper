"use client";
import React from 'react';

export default function DocumentList({ documents, refresh }: { documents: any[], refresh: () => void }) {
  if (!documents || documents.length === 0) {
    return (
      <div className="bg-white p-8 rounded-xl shadow border border-gray-100 mt-6 text-center text-gray-500">
        No documents uploaded yet.
      </div>
    );
  }

  const getStatusBadge = (status: string) => {
    switch (status.toLowerCase()) {
      case 'success': return <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded font-medium">Success</span>;
      case 'failed': return <span className="bg-red-100 text-red-800 text-xs px-2 py-1 rounded font-medium">Failed</span>;
      case 'processing': return <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded font-medium">Processing</span>;
      default: return <span className="bg-gray-100 text-gray-800 text-xs px-2 py-1 rounded font-medium">{status}</span>;
    }
  };

  return (
    <div className="bg-white rounded-xl shadow border border-gray-100 mt-6 overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-100 flex justify-between items-center bg-gray-50 cursor-pointer" onClick={refresh}>
        <h3 className="text-lg font-semibold text-gray-800">Uploaded Documents</h3>
        <button className="text-sm text-blue-600 hover:underline">Refresh ↻</button>
      </div>
      <ul className="divide-y divide-gray-100">
        {documents.map((doc) => (
          <li key={doc.id} className="p-6 hover:bg-gray-50 flex items-center justify-between">
            <div>
              <div className="flex items-center space-x-3 mb-1">
                <span className="font-medium text-gray-900">{doc.original_filename}</span>
                {getStatusBadge(doc.parse_status)}
              </div>
              <div className="text-sm text-gray-500 flex space-x-4">
                <span>{doc.document_type.replace('_', ' ').toUpperCase()}</span>
                <span>{(doc.file_size / 1024).toFixed(1)} KB</span>
                <span>{new Date(doc.created_at).toLocaleString()}</span>
              </div>
              {doc.parse_status === 'failed' && (
                <div className="mt-2 text-sm text-red-600 bg-red-50 p-2 rounded border border-red-100">
                  <span className="font-semibold">{doc.parse_error_code}:</span> {doc.parse_error_message}
                </div>
              )}
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
