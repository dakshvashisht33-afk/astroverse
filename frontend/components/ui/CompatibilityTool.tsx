'use client';

import { useState } from 'react';
import api, { getApiErrorMessage } from '@/lib/api';
import { useLanguage } from '@/lib/i18n';

const field = 'w-full rounded-xl border border-slate-700 bg-slate-950/70 px-3 py-3 text-sm text-white outline-none focus:border-indigo-400';
const SIGNS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces'];
const LORDS = ['Mars','Venus','Mercury','Moon','Sun','Mercury','Venus','Mars','Jupiter','Saturn','Saturn','Jupiter'];
const FRIENDS: Record<string,string[]> = {Sun:['Moon','Mars','Jupiter'],Moon:['Sun','Mercury'],Mars:['Sun','Moon','Jupiter'],Mercury:['Sun','Venus'],Jupiter:['Sun','Moon','Mars'],Venus:['Mercury','Saturn'],Saturn:['Mercury','Venus']};
const ENEMIES: Record<string,string[]> = {Sun:['Venus','Saturn'],Moon:[],Mars:['Mercury'],Mercury:['Moon'],Jupiter:['Mercury','Venus'],Venus:['Sun','Moon'],Saturn:['Sun','Moon','Mars']};

export default function CompatibilityTool({ profileId, ownName }: { profileId: string; ownName: string }) {
  const { t } = useLanguage();
  const [form, setForm] = useState({ full_name: '', dob: '', tob: '12:00', timezone: 'Asia/Kolkata', latitude: '28.6139', longitude: '77.2090', time_unknown: false });
  const [result, setResult] = useState<any>(null);
  const [scoringOrder, setScoringOrder] = useState<'a_bride_b_groom' | 'b_bride_a_groom'>('a_bride_b_groom');
  const [moonA, setMoonA] = useState(0);
  const [moonB, setMoonB] = useState(0);
  const moonDistance = (moonB - moonA + 12) % 12 + 1;
  const moonBhakoot = [2, 5, 6, 8, 9, 12].includes(moonDistance) ? 'Traditionally flagged' : 'Not flagged by the basic distance rule';
  const lordA = LORDS[moonA], lordB = LORDS[moonB];
  const relation = lordA === lordB ? 'Same Moon-sign lord' : (FRIENDS[lordA] || []).includes(lordB) && (FRIENDS[lordB] || []).includes(lordA) ? 'Mutual natural friends' : (ENEMIES[lordA] || []).includes(lordB) && (ENEMIES[lordB] || []).includes(lordA) ? 'Mutual natural enemies' : 'Mixed or neutral natural relationship';
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const update = (key: string, value: string | boolean) => setForm((old) => ({ ...old, [key]: value }));
  async function submit(event: React.FormEvent) {
    event.preventDefault(); setBusy(true); setError(''); setResult(null);
    try {
      const response = await api.post(`/compatibility/${profileId}`, { scoring_order: scoringOrder, partner: { ...form, latitude: Number(form.latitude), longitude: Number(form.longitude), dob: form.dob, tob: form.time_unknown ? '12:00' : form.tob } });
      setResult(response.data);
    } catch (e) { setError(getApiErrorMessage(e, 'Could not calculate this match.')); }
    finally { setBusy(false); }
  }
  return <section className="space-y-5">
    <div className="rounded-3xl border border-fuchsia-300/15 bg-gradient-to-br from-fuchsia-950/50 via-slate-900 to-indigo-950/50 p-6"><p className="text-xs font-semibold uppercase tracking-[0.2em] text-fuchsia-200">{t('Two-chart comparison')}</p><h2 className="mt-2 text-2xl font-bold text-white">{t('Kundli compatibility')}</h2><p className="mt-2 max-w-3xl text-sm leading-relaxed text-slate-300">{t('Compare your saved birth profile with another person using the traditional 36-point Ashtakoota method. Add the other person’s birth details below; an unknown birth time is treated as noon and can affect the result.')}</p></div>
    <form onSubmit={submit} className="grid gap-4 rounded-3xl border border-slate-700 bg-slate-900/85 p-5 sm:grid-cols-2">
      <label className="space-y-1 text-sm text-slate-300">{t('Partner name')}<input required value={form.full_name} onChange={(e)=>update('full_name',e.target.value)} className={field} placeholder={t('Name')}/></label>
      <label className="space-y-1 text-sm text-slate-300">{t('Date of birth')}<input required type="date" value={form.dob} onChange={(e)=>update('dob',e.target.value)} className={field}/></label>
      <label className="space-y-1 text-sm text-slate-300">{t('Time of birth')}<input type="time" disabled={form.time_unknown} value={form.tob} onChange={(e)=>update('tob',e.target.value)} className={field}/></label>
      <label className="flex items-center gap-2 self-end pb-3 text-sm text-slate-300"><input type="checkbox" checked={form.time_unknown} onChange={(e)=>update('time_unknown',e.target.checked)}/>{t('Birth time unknown')}</label>
      <label className="space-y-1 text-sm text-slate-300">Timezone<input required value={form.timezone} onChange={(e)=>update('timezone',e.target.value)} className={field} placeholder="Asia/Kolkata"/></label>
      <label className="space-y-1 text-sm text-slate-300">Latitude<input required type="number" step="any" value={form.latitude} onChange={(e)=>update('latitude',e.target.value)} className={field} placeholder="28.6139"/></label>
      <label className="space-y-1 text-sm text-slate-300">Longitude<input required type="number" step="any" value={form.longitude} onChange={(e)=>update('longitude',e.target.value)} className={field} placeholder="77.2090"/></label>
      <label className="space-y-1 text-sm text-slate-300">Traditional scoring orientation<select value={scoringOrder} onChange={(e)=>setScoringOrder(e.target.value as typeof scoringOrder)} className={field}><option value="a_bride_b_groom">My chart as bride · partner as groom</option><option value="b_bride_a_groom">My chart as groom · partner as bride</option></select></label>
      <button disabled={busy || !form.dob} className="self-end rounded-xl bg-indigo-600 px-5 py-3 font-semibold text-white transition hover:bg-indigo-500 disabled:opacity-50">{busy ? t('Calculating…') : t('Compare charts')}</button>
      <p className="sm:col-span-2 text-xs text-slate-500">Your saved profile: {ownName || 'My birth profile'}. Enter decimal coordinates for the other birthplace (for example, New Delhi 28.6139, 77.2090).</p>
    </form>
    {error && <p role="alert" className="rounded-xl border border-rose-400/20 bg-rose-950/30 p-4 text-sm text-rose-200">{error}</p>}
    <section className="rounded-3xl border border-slate-700 bg-slate-900/85 p-5"><p className="text-xs font-semibold uppercase tracking-widest text-indigo-300">For incomplete birth details</p><h3 className="mt-1 text-xl font-semibold text-white">Moon-sign comparison</h3><p className="mt-1 text-sm text-slate-400">If you only know both Moon signs, view two limited traditional indicators. This is not the full 36-point Kundli match.</p><div className="mt-4 grid gap-3 sm:grid-cols-2"><label className="text-sm text-slate-300">Your Moon sign<select value={moonA} onChange={(e)=>setMoonA(Number(e.target.value))} className={field}>{SIGNS.map((s,i)=><option key={s} value={i}>{s}</option>)}</select></label><label className="text-sm text-slate-300">Other Moon sign<select value={moonB} onChange={(e)=>setMoonB(Number(e.target.value))} className={field}>{SIGNS.map((s,i)=><option key={s} value={i}>{s}</option>)}</select></label></div><div className="mt-4 grid gap-3 sm:grid-cols-2"><div className="rounded-xl border border-slate-700 bg-slate-950/60 p-4"><p className="text-xs uppercase text-slate-500">Rashi distance indicator</p><p className="mt-1 font-semibold text-indigo-100">{moonBhakoot}</p><p className="mt-1 text-xs text-slate-400">{moonDistance} signs apart (directional). Traditional schools may interpret exceptions differently.</p></div><div className="rounded-xl border border-slate-700 bg-slate-950/60 p-4"><p className="text-xs uppercase text-slate-500">Moon-sign lords</p><p className="mt-1 font-semibold text-indigo-100">{lordA} · {relation} · {lordB}</p><p className="mt-1 text-xs text-slate-400">Uses classical natural relationships, without temporary friendship or a full chart.</p></div></div></section>
    {result && <div className="space-y-4 rounded-3xl border border-slate-700 bg-slate-900/85 p-5">
      <div className="flex flex-wrap items-end justify-between gap-3"><div><p className="text-xs uppercase tracking-widest text-indigo-300">Ashtakoota score</p><h3 className="mt-1 text-3xl font-bold text-white">{result.score}<span className="text-lg text-slate-400"> / {result.max_score}</span></h3></div><p className="max-w-lg text-sm text-slate-300">{result.threshold_note}</p></div>
      <div className="grid gap-3 sm:grid-cols-2">{Object.entries(result.people).map(([key, person]: [string, any])=><div key={key} className="rounded-2xl border border-slate-700 bg-slate-950/50 p-4"><p className="font-semibold text-indigo-100">{person.name}</p><p className="mt-1 text-sm text-slate-300">Moon: {person.moon_sign} · {person.nakshatra}, Pada {person.pada}</p></div>)}</div>
      <div className="overflow-x-auto rounded-xl border border-slate-700"><table className="w-full text-left text-sm"><thead className="bg-slate-800 text-xs uppercase text-slate-400"><tr><th className="p-3">Koota</th><th className="p-3">Score</th><th className="p-3">Basis</th></tr></thead><tbody>{result.kootas.map((k: any)=><tr key={k.name} className="border-t border-slate-800"><td className="p-3 font-medium text-white">{k.name}</td><td className="p-3 text-indigo-200">{k.score} / {k.max}</td><td className="p-3 text-slate-400">{k.detail}</td></tr>)}</tbody></table></div>
      <details className="rounded-xl border border-slate-700 p-4"><summary className="cursor-pointer font-semibold text-indigo-200">Mangal Dosha screening</summary><p className="mt-3 text-sm text-slate-300">{result.mangal_screening.method}</p><pre className="mt-2 overflow-auto text-xs text-slate-400">{JSON.stringify(result.mangal_screening, null, 2)}</pre></details>
      <p className="text-xs leading-relaxed text-slate-500">{result.method} {result.notice}</p>
    </div>}
  </section>;
}
