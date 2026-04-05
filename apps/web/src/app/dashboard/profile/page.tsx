"use client";
import React, { useEffect, useState } from 'react';

export default function ProfilePage() {
  const [profile, setProfile] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [editMode, setEditMode] = useState(false);
  const [formData, setFormData] = useState<any>(null);

  const fetchProfile = async () => {
    try {
      const resp = await fetch("http://localhost:8000/api/profile", {credentials: 'include'});
      if (resp.ok) {
        const data = await resp.json();
        setProfile(data);
        if(!formData) {
            setFormData(data.canonical_profile_json || {});
        }
      } else {
        setProfile(null);
      }
    } catch(e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchProfile();
    const interval = setInterval(() => {
      // only poll if building or we dont have profile yet
      fetchProfile();
    }, 5000);
    return () => clearInterval(interval);
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const handleBuild = async () => {
    await fetch("http://localhost:8000/api/profile/build", {method: 'POST', credentials: 'include'});
    setLoading(true);
    fetchProfile();
  }
  
  const handleSave = async () => {
    setLoading(true);
    try {
        const resp = await fetch("http://localhost:8000/api/profile", {
            method: 'PATCH', 
            credentials: 'include',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({canonical_profile_json: formData})
        });
        const data = await resp.json();
        setProfile(data);
        setEditMode(false);
    } catch(e) {
        console.error(e);
    } finally {
        setLoading(false);
    }
  }

  const identity = formData?.identity || {};
  const experience = formData?.experience || [];

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <header className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 tracking-tight">Canonical Profile</h1>
            <a href="/dashboard" className="text-blue-600 hover:text-blue-800 text-sm mt-1 inline-block">&larr; Back to Dashboard</a>
          </div>
          <div className="flex gap-4">
             {profile?.status === 'success' && !editMode && (
                <button onClick={() => setEditMode(true)} className="px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-md shadow-sm hover:bg-gray-50">
                  Edit Profile
                </button>
             )}
             {editMode && (
                <button onClick={handleSave} className="px-4 py-2 bg-green-600 text-white rounded-md shadow-sm hover:bg-green-700">
                  Save Changes
                </button>
             )}
            <button onClick={handleBuild} disabled={profile?.status === 'building'} className="px-4 py-2 bg-blue-600 text-white rounded-md shadow-sm hover:bg-blue-700 disabled:opacity-50">
              {profile?.status === 'building' ? 'Building...' : 'Build Profile'}
            </button>
          </div>
        </header>

        {loading && !profile && <div className="text-gray-500">Loading...</div>}

        {!loading && profile?.status === "building" && (
            <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-6">
                <p className="text-yellow-700">Profile is currently being semantic parsed and built. Please wait...</p>
            </div>
        )}

        {profile && profile.canonical_profile_json && (
          <div className="space-y-6">
            {profile.confidence_summary_json?.conflicts_resolved > 0 && (
                <div className="bg-blue-50 text-blue-700 p-4 rounded border border-blue-200 text-sm">
                    ⚠️ {profile.confidence_summary_json.conflicts_resolved} data conflicts were automatically resolved using merge precedence rules. Please review the profile carefully.
                </div>
            )}
            
            {/* Basic Info Card */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold mb-4 text-gray-800 border-b pb-2">Identity</h2>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-500">Name</label>
                  {editMode ? (
                      <input className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm border p-2" 
                             value={identity.name || ''} 
                             onChange={(e) => setFormData({...formData, identity: {...identity, name: e.target.value}})} />
                  ) : <p className="mt-1">{identity.name || "N/A"}</p>}
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-500">Email</label>
                  {editMode ? (
                      <input className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm border p-2" 
                             value={identity.email || ''} 
                             onChange={(e) => setFormData({...formData, identity: {...identity, email: e.target.value}})} />
                  ) : <p className="mt-1">{identity.email || "N/A"}</p>}
                </div>
                <div className="col-span-2">
                  <label className="block text-sm font-medium text-gray-500">Headline</label>
                  {editMode ? (
                      <input className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm border p-2" 
                             value={formData.headline || ''} 
                             onChange={(e) => setFormData({...formData, headline: e.target.value})} />
                  ) : <p className="mt-1">{formData.headline || "N/A"}</p>}
                </div>
                <div className="col-span-2">
                  <label className="block text-sm font-medium text-gray-500">Summary</label>
                  {editMode ? (
                      <textarea className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm border p-2 h-24" 
                             value={formData.summary || ''} 
                             onChange={(e) => setFormData({...formData, summary: e.target.value})} />
                  ) : <p className="mt-1 text-sm text-gray-700">{formData.summary || "N/A"}</p>}
                </div>
              </div>
            </div>

            {/* Experience Card */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold mb-4 text-gray-800 border-b pb-2">Experience</h2>
              <div className="space-y-6">
                 {experience.map((exp: any, i: number) => (
                    <div key={i} className="border-b last:border-0 pb-4">
                        {editMode ? (
                            <div className="grid grid-cols-2 gap-4">
                                <div><label className="text-xs text-gray-500">Company</label><input className="w-full border p-1 text-sm" value={exp.company} onChange={e => {const newE = [...experience]; newE[i].company = e.target.value; setFormData({...formData, experience: newE})}}/></div>
                                <div><label className="text-xs text-gray-500">Title</label><input className="w-full border p-1 text-sm" value={exp.title} onChange={e => {const newE = [...experience]; newE[i].title = e.target.value; setFormData({...formData, experience: newE})}}/></div>
                                <div><label className="text-xs text-gray-500">Start Date</label><input className="w-full border p-1 text-sm" value={exp.start_date || ""} onChange={e => {const newE = [...experience]; newE[i].start_date = e.target.value; setFormData({...formData, experience: newE})}}/></div>
                                <div><label className="text-xs text-gray-500">End Date</label><input className="w-full border p-1 text-sm" value={exp.end_date || ""} onChange={e => {const newE = [...experience]; newE[i].end_date = e.target.value; setFormData({...formData, experience: newE})}}/></div>
                            </div>
                        ) : (
                            <>
                                <h3 className="font-semibold text-lg">{exp.title} <span className="text-gray-500 font-normal">at {exp.company}</span></h3>
                                <div className="text-sm text-gray-500 mb-2">{exp.start_date} - {exp.end_date || "Present"}</div>
                                <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
                                    {(exp.bullets || []).map((b: string, j: number) => <li key={j}>{b}</li>)}
                                </ul>
                            </>
                        )}
                    </div>
                 ))}
                 {experience.length === 0 && <p className="text-gray-500 italic text-sm">No experience entries found.</p>}
              </div>
            </div>

            {/* Skills */}
            <div className="bg-white rounded-lg shadow p-6">
               <h2 className="text-xl font-semibold mb-4 text-gray-800 border-b pb-2">Skills</h2>
               <div className="flex flex-wrap gap-2">
                 {(formData.skills || []).map((s: string, i: number) => (
                    <span key={i} className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                        {s}
                    </span>
                 ))}
               </div>
               {editMode && <p className="text-xs text-gray-400 mt-2">Editing list of skills directly is temporarily disabled in this UI.</p>}
            </div>

          </div>
        )}
      </div>
    </div>
  );
}
