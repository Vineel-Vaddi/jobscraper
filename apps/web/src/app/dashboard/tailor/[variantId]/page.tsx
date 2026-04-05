import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function TailorVariantPage({ params }: { params: { variantId: string } }) {
  const [variant, setVariant] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const router = useRouter();
  
  const variantId = params.variantId;

  const fetchVariant = async () => {
    try {
      const resp = await fetch(`http://localhost:8000/api/resume-variants/${variantId}`, { credentials: 'include' });
      if (resp.ok) {
        setVariant(await resp.json());
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
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

  if (loading && !variant) return <div className="p-8">Loading...</div>;
  if (!variant) return <div className="p-8">Variant not found.</div>;

  const isComplete = !['pending', 'processing'].includes(variant.status);
  
  const tailored = variant.tailored_resume_json ? JSON.parse(variant.tailored_resume_json) : null;
  const ats = variant.ats_score_json ? JSON.parse(variant.ats_score_json) : null;
  const validator = variant.validator_report_json ? JSON.parse(variant.validator_report_json) : null;

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-5xl mx-auto">
        <header className="mb-8 flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-900 tracking-tight">Tailored Resume Output</h1>
          <a href="/dashboard/jobs" className="text-blue-600 hover:text-blue-800">Back to Jobs</a>
        </header>

        {!isComplete ? (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center">
             <div className="text-blue-500 text-xl font-medium mb-2">Generating Tailored Resume...</div>
             <p className="text-gray-500">Currently executing safety and truth-validation models.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="md:col-span-2">
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden p-8 mb-6">
                 <h2 className="text-xl font-bold border-b pb-4 mb-4">Preview</h2>
                 {tailored ? (
                   <div className="prose max-w-none text-sm text-gray-800">
                      <div className="text-center mb-6">
                        <h3 className="text-2xl font-bold m-0">{tailored.contact?.name || 'Applicant'}</h3>
                        <p className="text-gray-500 m-0">{tailored.contact?.email} | {tailored.contact?.phone} | {tailored.contact?.location}</p>
                      </div>
                      
                      {tailored.summary?.summary_text && (
                        <div className="mb-6">
                          <h4 className="border-b font-bold uppercase tracking-wider text-xs mb-2">Professional Summary</h4>
                          <p>{tailored.summary.summary_text}</p>
                        </div>
                      )}
                      
                      {tailored.skills && (
                        <div className="mb-6">
                          <h4 className="border-b font-bold uppercase tracking-wider text-xs mb-2">Technical Skills</h4>
                          <p>{tailored.skills.join(', ')}</p>
                        </div>
                      )}
                      
                      <div className="mb-6">
                         <h4 className="border-b font-bold uppercase tracking-wider text-xs mb-4">Experience</h4>
                         {tailored.experience?.map((exp: any, i: number) => (
                           <div key={i} className="mb-4">
                             <div className="flex justify-between font-bold text-gray-900">
                               <span>{exp.title}</span>
                               <span>{exp.start_date} - {exp.end_date || 'Present'}</span>
                             </div>
                             <div className="text-gray-600 italic mb-2">{exp.company}</div>
                             <ul className="list-disc pl-5">
                               {exp.bullets?.map((b: string, j: number) => <li key={j}>{b}</li>)}
                             </ul>
                           </div>
                         ))}
                      </div>
                   </div>
                 ) : (
                   <div className="text-red-500">Failed to render parsed JSON.</div>
                 )}
              </div>
            </div>

            <div className="space-y-6">
              {variant.status === "failed" && (
                <div className="bg-red-50 border-red-200 border p-4 rounded-lg">
                  <h3 className="text-red-700 font-bold mb-1">Variant Generation Failed</h3>
                  <p className="text-red-600 text-sm whitespace-pre-wrap">{variant.error_message}</p>
                </div>
              )}
            
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <h3 className="font-bold text-lg mb-4 text-gray-900 border-b pb-2">Truth Validator</h3>
                {validator ? (
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                       {validator.status === 'pass' ? (
                          <span className="bg-green-100 text-green-800 text-xs font-bold px-2 py-1 rounded">PASS</span>
                       ) : (
                          <span className="bg-red-100 text-red-800 text-xs font-bold px-2 py-1 rounded">NEEDS REVISION</span>
                       )}
                    </div>
                    <p className="text-xs text-gray-500 leading-relaxed mb-4">{validator.message}</p>
                    
                    {validator.unsupported_claims?.length > 0 && (
                      <div>
                        <div className="text-xs font-bold uppercase text-red-700 mb-1">Unsupported Claims Detected</div>
                        <div className="flex flex-wrap gap-1">
                          {validator.unsupported_claims.map((uc: string, i: number) => (
                             <span key={i} className="px-2 py-1 bg-red-50 border border-red-100 text-red-600 rounded text-xs">{uc}</span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="text-xs text-gray-500">Validation data unavailable.</div>
                )}
              </div>

              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <h3 className="font-bold text-lg mb-4 text-gray-900 border-b pb-2">ATS Scoring</h3>
                {ats ? (
                   <div>
                     <div className="flex justify-between items-baseline mb-4">
                        <span className="text-sm font-medium text-gray-600">Keyword Coverage</span>
                        <span className="text-3xl font-extrabold text-blue-600">{ats.coverage_percentage}%</span>
                     </div>
                     {ats.missing_critical_terms?.length > 0 && (
                       <div>
                         <div className="text-xs font-bold uppercase text-orange-700 mb-1">Missing Targeted Keywords</div>
                         <div className="flex flex-wrap gap-1">
                           {ats.missing_critical_terms.map((mis: string, i: number) => (
                              <span key={i} className="px-2 py-1 bg-orange-50 border border-orange-100 text-orange-600 rounded text-xs">{mis}</span>
                           ))}
                         </div>
                       </div>
                     )}
                   </div>
                ) : (
                  <div className="text-xs text-gray-500">ATS data unavailable.</div>
                )}
              </div>
              
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                 <h3 className="font-bold text-lg mb-4 text-gray-900 border-b pb-2">Exports</h3>
                 <div className="flex flex-col gap-3">
                   <a 
                     href={`http://localhost:8000/api/resume-variants/${variantId}/download/docx`}
                     className="w-full block text-center bg-blue-50 text-blue-700 font-medium py-2 rounded border border-blue-200 hover:bg-blue-100 transition"
                   >
                     Download DOCX
                   </a>
                   <a 
                     href={`http://localhost:8000/api/resume-variants/${variantId}/download/pdf`}
                     className="w-full block text-center bg-blue-50 text-blue-700 font-medium py-2 rounded border border-blue-200 hover:bg-blue-100 transition"
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
