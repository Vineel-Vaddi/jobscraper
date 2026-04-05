import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function ReviewVariantPage({ params }: { params: { variantId: string } }) {
  const [variant, setVariant] = useState<any>(null);
  const [reviewData, setReviewData] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [applying, setApplying] = useState<boolean>(false);
  const router = useRouter();
  
  const variantId = params.variantId;

  const fetchVariant = async () => {
    try {
      const resp = await fetch(`http://localhost:8000/api/resume-variants/${variantId}`, { credentials: 'include' });
      if (resp.ok) {
        const data = await resp.json();
        setVariant(data);
        if (['success', 'needs_review'].includes(data.status)) {
            fetchReviewData();
        }
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const fetchReviewData = async () => {
    try {
      const resp = await fetch(`http://localhost:8000/api/resume-variants/${variantId}/review`, { credentials: 'include' });
      if (resp.ok) {
        setReviewData(await resp.json());
      }
    } catch (e) {
       console.error(e);
    }
  };

  useEffect(() => {
    fetchVariant();
    const interval = setInterval(() => {
      setVariant((curr: any) => {
        if (!curr || ['pending', 'processing'].includes(curr.status)) {
          fetchVariant();
        }
        return curr;
      });
    }, 3000);
    return () => clearInterval(interval);
  }, [variantId]);

  const handleApply = async () => {
      setApplying(true);
      try {
        const resp = await fetch(`http://localhost:8000/api/resume-variants/${variantId}/go-apply`, { 
            method: 'POST',
            credentials: 'include' 
        });
        if (resp.ok) {
            const data = await resp.json();
            if (data.target_url) {
                window.open(data.target_url, "_blank");
            } else {
                alert("No external link stored for this job.");
            }
        }
      } catch (e) {
          console.error(e);
      } finally {
          setApplying(false);
      }
  };

  const trackEvent = async (eventType: string) => {
      try {
          await fetch(`http://localhost:8000/api/resume-variants/${variantId}/events`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              credentials: 'include',
              body: JSON.stringify({ event_type: eventType })
          });
      } catch (e) {
          console.error("Failed to track", e);
      }
  };

  if (loading && !variant) return <div className="p-8">Loading...</div>;
  if (!variant) return <div className="p-8">Variant not found.</div>;

  const isComplete = !['pending', 'processing'].includes(variant.status);

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        <header className="mb-8 flex justify-between items-center bg-white p-4 rounded-xl shadow-sm border border-gray-200">
          <div>
              <h1 className="text-2xl font-bold text-gray-900 tracking-tight">Review & Apply</h1>
              <p className="text-sm text-gray-500">Compare what changed from your master profile.</p>
          </div>
          <div className="flex gap-4">
              <a href="/dashboard/jobs" className="text-gray-600 hover:text-gray-900 font-medium self-center">Back</a>
              {isComplete && (
                <button
                  onClick={handleApply}
                  disabled={applying}
                  className="bg-blue-600 text-white px-6 py-2 rounded-lg font-bold hover:bg-blue-700 disabled:opacity-50"
                >
                  {applying ? 'Launching...' : 'Go Apply'}
                </button>
              )}
          </div>
        </header>

        {!isComplete ? (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center mt-12">
             <div className="text-blue-500 text-xl font-medium mb-2">Generating Tailored Resume...</div>
             <p className="text-gray-500">Currently executing diff engines and truth-validation models.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2 space-y-6">
                
              {variant.status === "failed" && (
                <div className="bg-red-50 border-red-200 border p-4 rounded-lg">
                  <h3 className="text-red-700 font-bold mb-1">Variant Generation Failed</h3>
                  <p className="text-red-600 text-sm whitespace-pre-wrap">{variant.error_message}</p>
                </div>
              )}

              {reviewData && reviewData.section_diffs && (
                  <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                      <div className="p-6 border-b border-gray-200 bg-gray-50">
                          <h2 className="text-lg font-bold">Document Diff Analysis</h2>
                      </div>
                      <div className="p-6 space-y-8">
                          {reviewData.section_diffs.map((section: any, i: number) => (
                              <div key={i} className="border border-gray-100 rounded-lg p-4">
                                  <div className="flex justify-between items-center mb-4 border-b pb-2">
                                      <h3 className="font-bold text-gray-800">{section.section_name}</h3>
                                      {section.status === 'modified' && <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded font-bold">MODIFIED</span>}
                                      {section.status === 'added' && <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded font-bold">ADDED</span>}
                                      {section.status === 'unchanged' && <span className="bg-gray-100 text-gray-800 text-xs px-2 py-1 rounded font-bold">UNCHANGED</span>}
                                  </div>
                                  <ul className="space-y-2">
                                      {section.bullets.map((b: any, j: number) => (
                                          <li key={j} className="text-sm flex items-start gap-2">
                                              {b.type === 'added' && <span className="text-green-600 font-bold w-4">+</span>}
                                              {b.type === 'rewritten' && <span className="text-blue-600 font-bold w-4">~</span>}
                                              {b.type === 'unchanged' && <span className="text-gray-400 font-bold w-4">=</span>}
                                              <span className={b.type === 'added' ? 'text-green-800 bg-green-50' : b.type === 'rewritten' ? 'text-blue-800 bg-blue-50' : 'text-gray-600'}>
                                                  {b.text}
                                              </span>
                                          </li>
                                      ))}
                                  </ul>
                              </div>
                          ))}
                      </div>
                  </div>
              )}
            </div>

            <div className="space-y-6">
                
              {reviewData && reviewData.why_changed_notes && (
                  <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 border-l-4 border-l-blue-500">
                      <h3 className="font-bold text-gray-900 border-b pb-2 mb-4">Why Things Changed</h3>
                      <ul className="space-y-3">
                          {reviewData.why_changed_notes.map((note: string, i: number) => (
                              <li key={i} className="text-sm text-gray-600 flex items-start gap-2">
                                  <span className="text-blue-500 mt-0.5">•</span> 
                                  <span>{note}</span>
                              </li>
                          ))}
                      </ul>
                  </div>
              )}

              {reviewData && reviewData.validator_summary && (
                <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                  <h3 className="font-bold text-gray-900 border-b pb-2 mb-4">Truth Validator</h3>
                  <div className="flex items-center gap-2 mb-2">
                     {reviewData.validator_summary.status === 'pass' ? (
                        <span className="bg-green-100 text-green-800 text-xs font-bold px-2 py-1 rounded">PASS</span>
                     ) : (
                        <span className="bg-red-100 text-red-800 text-xs font-bold px-2 py-1 rounded">NEEDS REVISION</span>
                     )}
                  </div>
                  <p className="text-xs text-gray-500 leading-relaxed mb-4">{reviewData.validator_summary.message}</p>
                  
                  {reviewData.validator_summary.unsupported_claims?.length > 0 && (
                    <div>
                      <div className="text-xs font-bold uppercase text-red-700 mb-1">Unsupported Claims Detected</div>
                      <div className="flex flex-wrap gap-1">
                        {reviewData.validator_summary.unsupported_claims.map((uc: string, i: number) => (
                           <span key={i} className="px-2 py-1 bg-red-50 border border-red-100 text-red-600 rounded text-xs">{uc}</span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
              
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                 <h3 className="font-bold text-gray-900 border-b pb-2 mb-4">Downloads & Actions</h3>
                 <div className="flex flex-col gap-3">
                   <a 
                     href={`http://localhost:8000/api/resume-variants/${variantId}/download/docx`}
                     onClick={() => trackEvent('download_docx')}
                     className="w-full block text-center bg-gray-50 text-gray-700 font-medium py-2 rounded border border-gray-200 hover:bg-gray-100 transition"
                   >
                     Download DOCX
                   </a>
                   <a 
                     href={`http://localhost:8000/api/resume-variants/${variantId}/download/pdf`}
                     onClick={() => trackEvent('download_pdf')}
                     className="w-full block text-center bg-gray-50 text-gray-700 font-medium py-2 rounded border border-gray-200 hover:bg-gray-100 transition"
                   >
                     Download PDF
                   </a>
                 </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
