import React, { useState, useEffect } from 'react';

export default function PreferencesPage() {
  const [prefs, setPrefs] = useState<any>(null);
  const [titles, setTitles] = useState<any[]>([]);
  const [presets, setPresets] = useState<any[]>([]);
  const [pins, setPins] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const [form, setForm] = useState({
    preferred_locations: '',
    preferred_work_modes: '',
    target_seniority: '',
    salary_notes: '',
    resume_emphasis: '',
    exclude_keywords: '',
  });

  // New preset form
  const [newPreset, setNewPreset] = useState({ name: '', target_titles: '', priority_skills: '', summary_focus: '' });

  useEffect(() => {
    Promise.all([
      fetch('http://localhost:8000/api/profile/preferences', { credentials: 'include' }).then(r => r.json()),
      fetch('http://localhost:8000/api/profile/suggested-titles', { credentials: 'include' }).then(r => r.ok ? r.json() : []).catch(() => []),
      fetch('http://localhost:8000/api/presets', { credentials: 'include' }).then(r => r.json()),
      fetch('http://localhost:8000/api/pins', { credentials: 'include' }).then(r => r.json()),
    ]).then(([p, t, pr, pi]) => {
      setPrefs(p);
      setTitles(t);
      setPresets(pr);
      setPins(pi);
      setForm({
        preferred_locations: (p.preferred_locations || []).join(', '),
        preferred_work_modes: (p.preferred_work_modes || []).join(', '),
        target_seniority: p.target_seniority || '',
        salary_notes: p.salary_notes || '',
        resume_emphasis: p.resume_emphasis || '',
        exclude_keywords: (p.exclude_keywords || []).join(', '),
      });
    }).catch(console.error).finally(() => setLoading(false));
  }, []);

  const savePrefs = async () => {
    setSaving(true);
    const split = (s: string) => s.split(',').map(v => v.trim()).filter(Boolean);
    await fetch('http://localhost:8000/api/profile/preferences', {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({
        preferred_locations: split(form.preferred_locations),
        preferred_work_modes: split(form.preferred_work_modes),
        target_seniority: form.target_seniority || null,
        salary_notes: form.salary_notes || null,
        resume_emphasis: form.resume_emphasis || null,
        exclude_keywords: split(form.exclude_keywords),
      }),
    });
    setSaving(false);
  };

  const createPreset = async () => {
    const split = (s: string) => s.split(',').map(v => v.trim()).filter(Boolean);
    const resp = await fetch('http://localhost:8000/api/presets', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({
        name: newPreset.name,
        target_titles: split(newPreset.target_titles),
        priority_skills: split(newPreset.priority_skills),
        summary_focus: newPreset.summary_focus || null,
      }),
    });
    if (resp.ok) {
      const p = await resp.json();
      setPresets(prev => [p, ...prev]);
      setNewPreset({ name: '', target_titles: '', priority_skills: '', summary_focus: '' });
    }
  };

  const deletePreset = async (id: number) => {
    await fetch(`http://localhost:8000/api/presets/${id}`, { method: 'DELETE', credentials: 'include' });
    setPresets(prev => prev.filter(p => p.id !== id));
  };

  const deletePin = async (id: number) => {
    await fetch(`http://localhost:8000/api/pins/${id}`, { method: 'DELETE', credentials: 'include' });
    setPins(prev => prev.filter(p => p.id !== id));
  };

  if (loading) return <div className="p-8">Loading preferences...</div>;

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto space-y-8">
        <h1 className="text-2xl font-bold text-gray-900">Preferences & Presets</h1>

        {/* Preferences */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-bold mb-4">Targeting Preferences</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[
              { label: 'Preferred Locations (comma-separated)', key: 'preferred_locations' },
              { label: 'Work Modes (remote, hybrid, onsite)', key: 'preferred_work_modes' },
              { label: 'Target Seniority', key: 'target_seniority' },
              { label: 'Salary Notes', key: 'salary_notes' },
              { label: 'Resume Emphasis (e.g. backend, ml)', key: 'resume_emphasis' },
              { label: 'Exclude Keywords (comma-separated)', key: 'exclude_keywords' },
            ].map(f => (
              <div key={f.key}>
                <label className="text-xs font-bold uppercase text-gray-500 block mb-1">{f.label}</label>
                <input
                  value={(form as any)[f.key]}
                  onChange={e => setForm(prev => ({ ...prev, [f.key]: e.target.value }))}
                  className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm"
                />
              </div>
            ))}
          </div>
          <button onClick={savePrefs} disabled={saving} className="mt-4 bg-blue-600 text-white px-6 py-2 rounded-lg font-medium text-sm hover:bg-blue-700 disabled:opacity-50">
            {saving ? 'Saving...' : 'Save Preferences'}
          </button>
        </div>

        {/* Suggested Titles */}
        {titles.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-bold mb-4">Suggested Target Titles</h2>
          <div className="flex flex-wrap gap-3">
            {titles.map((t: any, i: number) => (
              <div key={i} className="bg-blue-50 border border-blue-200 rounded-lg px-4 py-2">
                <div className="font-bold text-blue-900 text-sm">{t.title}</div>
                <div className="text-xs text-blue-600">{t.rationale}</div>
              </div>
            ))}
          </div>
        </div>
        )}

        {/* Role Presets */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-bold mb-4">Role Presets</h2>
          {presets.length > 0 && (
            <div className="space-y-3 mb-6">
              {presets.map(p => (
                <div key={p.id} className="flex justify-between items-center bg-gray-50 border rounded-lg p-3">
                  <div>
                    <span className="font-bold text-sm">{p.name}</span>
                    <span className="text-xs text-gray-500 ml-2">{(p.target_titles || []).join(', ')}</span>
                  </div>
                  <button onClick={() => deletePreset(p.id)} className="text-red-500 text-xs font-bold hover:underline">Delete</button>
                </div>
              ))}
            </div>
          )}
          <div className="border-t pt-4 grid grid-cols-1 md:grid-cols-2 gap-3">
            <input placeholder="Preset name (e.g. Backend)" value={newPreset.name} onChange={e => setNewPreset(p => ({...p, name: e.target.value}))} className="border rounded-lg px-3 py-2 text-sm" />
            <input placeholder="Target titles (comma-sep)" value={newPreset.target_titles} onChange={e => setNewPreset(p => ({...p, target_titles: e.target.value}))} className="border rounded-lg px-3 py-2 text-sm" />
            <input placeholder="Priority skills (comma-sep)" value={newPreset.priority_skills} onChange={e => setNewPreset(p => ({...p, priority_skills: e.target.value}))} className="border rounded-lg px-3 py-2 text-sm" />
            <input placeholder="Summary focus" value={newPreset.summary_focus} onChange={e => setNewPreset(p => ({...p, summary_focus: e.target.value}))} className="border rounded-lg px-3 py-2 text-sm" />
          </div>
          <button onClick={createPreset} disabled={!newPreset.name} className="mt-3 bg-gray-900 text-white px-5 py-2 rounded-lg text-sm font-medium disabled:opacity-30">Create Preset</button>
        </div>

        {/* Active Pins */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-bold mb-4">Active Resume Pins</h2>
          {pins.length > 0 ? (
            <div className="space-y-2">
              {pins.map(p => (
                <div key={p.id} className="flex justify-between items-center bg-gray-50 border rounded-lg p-3">
                  <div>
                    <span className="text-xs font-bold uppercase text-gray-500">{p.source_type}</span>
                    <span className="text-sm ml-2">{p.label || p.source_ref}</span>
                    <span className="ml-2 text-xs bg-blue-100 text-blue-800 px-2 py-0.5 rounded">{p.pin_mode}</span>
                  </div>
                  <button onClick={() => deletePin(p.id)} className="text-red-500 text-xs font-bold hover:underline">Remove</button>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-400 text-sm">No pins set. Pin sections or bullets from the tailoring review page.</p>
          )}
        </div>
      </div>
    </div>
  );
}
