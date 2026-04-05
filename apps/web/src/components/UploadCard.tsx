"use client";
import React, { useState } from 'react';

export default function UploadCard({ title, documentType, onUploadSuccess }: { title: string, documentType: string, onUploadSuccess: () => void }) {
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [message, setMessage] = useState({ text: "", type: "" });

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;

    setIsUploading(true);
    setMessage({ text: "", type: "" });

    const formData = new FormData();
    formData.append("file", file);
    formData.append("document_type", documentType);

    try {
      const resp = await fetch("http://localhost:8000/api/documents/upload", {
        method: "POST",
        body: formData,
        // credentials: "omit" - if backend allows CORS, wait, it requires withCredentials for session, but session is cookie.
        // Actually, if we use cookie based auth, we need withCredentials. Assuming we are running on localhost:3000, we need it.
      });
      // The API doesn't know about cors origins if nextjs runs on 3001, but we set it to 3000.
      if (!resp.ok) {
        throw new Error("Upload failed. Session might be invalid or file too large.");
      }
      setMessage({ text: "Upload successful. Parsing started.", type: "success" });
      setFile(null);
      if (documentType === 'resume') {
        (document.getElementById('file-upload-resume') as HTMLInputElement).value = '';
      } else {
        (document.getElementById(`file-upload-${documentType}`) as HTMLInputElement).value = '';
      }
      onUploadSuccess();
    } catch (err: any) {
      setMessage({ text: err.message, type: "error" });
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="bg-white p-6 rounded-xl shadow border border-gray-100 flex flex-col items-start transition-all hover:shadow-md">
      <h3 className="text-lg font-semibold mb-2 text-gray-800">{title}</h3>
      <p className="text-sm text-gray-500 mb-6">Upload your {title.toLowerCase()} for ingestion.</p>
      
      <form onSubmit={handleUpload} className="w-full flex items-center mb-4">
        <input 
          id={`file-upload-${documentType}`}
          type="file" 
          accept={documentType === 'resume' ? '.pdf,.docx' : '.zip,.pdf'}
          onChange={(e) => setFile(e.target.files ? e.target.files[0] : null)}
          className="block w-full text-sm text-gray-500
            file:mr-4 file:py-2 file:px-4
            file:rounded-full file:border-0
            file:text-sm file:font-semibold
            file:bg-blue-50 file:text-blue-700
            hover:file:bg-blue-100 cursor-pointer outline-none"
        />
        <button 
          disabled={!file || isUploading}
          className="ml-4 px-6 py-2 bg-blue-600 text-white rounded-full text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed transition"
        >
          {isUploading ? 'Uploading...' : 'Upload'}
        </button>
      </form>
      {message.text && (
        <div className={`mt-2 text-sm font-medium ${message.type === 'error' ? 'text-red-500' : 'text-green-600'}`}>
          {message.text}
        </div>
      )}
    </div>
  );
}
