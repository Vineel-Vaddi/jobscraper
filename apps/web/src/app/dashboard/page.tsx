"use client";
import React, { useEffect, useState } from 'react';
import UploadCard from '@/components/UploadCard';
import DocumentList from '@/components/DocumentList';

export default function Dashboard() {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchDocuments = async () => {
    try {
      const resp = await fetch("http://localhost:8000/api/documents", {credentials: 'include'});
      if (resp.ok) {
        const data = await resp.json();
        setDocuments(data);
      }
    } catch (e) {
      console.error("Failed to fetch documents", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
    // Simple polling
    const interval = setInterval(fetchDocuments, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-5xl mx-auto">
        <header className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 tracking-tight">Dashboard</h1>
          <button 
            onClick={() => {
               fetch('http://localhost:8000/api/auth/logout', {method: 'POST', credentials: 'include'})
               .then(() => window.location.href = '/');
            }} 
            className="text-gray-500 hover:text-gray-900 font-medium"
          >
            Sign Out
          </button>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <UploadCard 
            title="Resume" 
            documentType="resume" 
            onUploadSuccess={fetchDocuments} 
          />
          <UploadCard 
            title="LinkedIn Export" 
            documentType="linkedin_export" 
            onUploadSuccess={fetchDocuments} 
          />
        </div>

        {loading ? (
          <div className="mt-8 text-center text-gray-500">Loading documents...</div>
        ) : (
          <DocumentList documents={documents} refresh={fetchDocuments} />
        )}
      </div>
    </div>
  );
}
