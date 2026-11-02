'use client';

import React, { useMemo, useState } from 'react';
import NatalChart, { type ChartStyle, type VargaChartData } from '@/components/ui/NatalChart';
import { useLanguage } from '@/lib/i18n';

const features = [
  'Lagna & Chandra Charts', 'Chalit Table & Chart', 'Prastharashtakavarga Table', 'Ashtak Varga Table',
  'Aspect On Bhav Madhya', 'Aspect On KP Cusp', 'Shodashvarga Charts', 'Friendship Table',
  'Vimshottari Dasha', 'Shadbala & Bhavbala', 'Char Dasha', 'Yogini Dasha', 'Western System',
  'Print Sarvatobhadra Chakra', 'Transit Today', 'Dosha & Sade Sati Checks', 'Lal Kitab Chart & Planets Houses', 'Quick Calculators',
];
const cls = 'rounded-xl border border-slate-700 bg-slate-900/80 p-4';
const tableCls = 'w-full min-w-max text-left text-sm';
const thCls = 'bg-slate-800 px-3 py-2 text-xs uppercase tracking-wide text-slate-400';
const tdCls = 'border-t border-slate-800 px-3 py-2 text-slate-300';

function Table({ headers, rows }: { headers: string[]; rows: React.ReactNode[][] }) {
  return <div className="overflow-x-auto rounded-xl border border-slate-700"><table className={tableCls}><thead><tr>{headers.map((h) => <th className={thCls} key={h}>{h}</th>)}</tr></thead><tbody>{rows.map((r, i) => <tr key={i}>{r.map((v, j) => <td className={tdCls} key={j}>{v}</td>)}</tr>)}</tbody></table></div>;
}

function ChartTable({ chart }: { chart: any }) {
  if (!chart) return <p className="text-amber-200">Birth time is unknown; this Lagna-based chart cannot be calculated.</p>;
  const byHouse = Array.from({ length: 12 }, (_, i) => {
    const house = i + 1;
    const placements = chart.planets.filter((p: any) => p.house === house);
    return [house, placements[0]?.sign || '—', placements.map((p: any) => `${p.planet} ${Number(p.degree).toFixed(1)}°`).join(', ') || '—'];
  });
  return <div><p className="mb-3 text-sm text-slate-400">{chart.reference} sign: <span className="text-indigo-200">{chart.reference_sign || 'unavailable'}</span> · Whole-sign houses from the reference sign.</p><Table headers={['House', 'Sign', 'Grahas and degrees']} rows={byHouse} /></div>;
}

export default function AstrologySuite({ data, error }: { data: any; error?: string | null }) {
  const { t } = useLanguage();
  const [feature, setFeature] = useState(features[0]);
  const [chartMode, setChartMode] = useState<'lagna' | 'chandra'>('lagna');
  const [chartStyle, setChartStyle] = useState<ChartStyle>('north');
  const [bavPlanet, setBavPlanet] = useState('Sun');
  const [calcName, setCalcName] = useState('');
  const [calcDob, setCalcDob] = useState('');
  const rowsForPeriods = (periods: any[] = []) => periods.map((p) => [p.lord || p.yogini, p.sign || '—', p.start, p.end, p.years ?? '—']);
  const transitRows = useMemo(() => Object.entries(data?.transits?.positions || {}).map(([p, v]: [string, any]) => [p, v.sign, `${v.degree.toFixed(2)}°`, v.retrograde ? 'Retrograde' : 'Direct']), [data]);

  if (!data) return <section className={`${cls} text-sm ${error ? 'text-amber-200' : 'text-slate-400'}`}>{error || t('Loading the chart tools…')}</section>;

  let body: React.ReactNode = null;
  if (feature === 'Quick Calculators') {
    const planets = data.lagna_chart?.planets || [];
    const sun = planets.find((p: any) => p.planet === 'Sun');
    const moon = planets.find((p: any) => p.planet === 'Moon');
    const nakshatra = data.vimshottari?.birth_nakshatra;
    const reduce = (value: number) => { let n = value; while (n > 9) n = String(n).split('').reduce((sum, d) => sum + Number(d), 0); return n; };
    const nameTotal = calcName.toUpperCase().replace(/[^A-Z]/g, '').split('').reduce((sum, c) => sum + ((c.charCodeAt(0) - 65) % 9) + 1, 0);
    const lifePath = calcDob ? reduce(calcDob.replaceAll('-', '').split('').reduce((sum, d) => sum + Number(d), 0)) : null;
    body = <div className="space-y-5"><p className="text-sm leading-relaxed text-slate-400">Standalone results from your saved birth chart, plus simple numerology calculators.</p>
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">{[['Sun sign', sun?.sign || '—', 'Lahiri sidereal'], ['Moon sign', moon?.sign || '—', 'Lahiri sidereal'], ['Ascendant', data.lagna_chart?.reference_sign || 'Birth time required', 'Whole-sign chart'], ['Nakshatra', nakshatra?.name || '—', nakshatra?.pada ? `Pada ${nakshatra.pada}` : 'Moon longitude']].map(([label, value, note]) => <article key={label} className="rounded-2xl border border-slate-700 bg-slate-950/50 p-4"><p className="text-xs uppercase tracking-wide text-slate-500">{label}</p><p className="mt-2 text-xl font-semibold text-indigo-100">{value}</p><p className="mt-1 text-xs text-slate-500">{note}</p></article>)}</div>
      <div className="grid gap-4 md:grid-cols-2"><section className="rounded-2xl border border-slate-700 bg-slate-950/40 p-5"><h3 className="font-semibold text-white">Name number</h3><p className="mt-1 text-xs text-slate-400">Pythagorean letter values (a numerology convention).</p><input aria-label="Name for numerology" value={calcName} onChange={(e)=>setCalcName(e.target.value)} className="mt-4 w-full rounded-xl border border-slate-700 bg-slate-900 px-3 py-3 text-white" placeholder="Enter a name"/>{calcName && <p className="mt-3 text-sm text-indigo-100">Name number: <strong>{reduce(nameTotal)}</strong> <span className="text-slate-400">(total {nameTotal})</span></p>}</section>
      <section className="rounded-2xl border border-slate-700 bg-slate-950/40 p-5"><h3 className="font-semibold text-white">Life path number</h3><p className="mt-1 text-xs text-slate-400">Reduce the digits in the date of birth to one digit.</p><input aria-label="Date of birth for numerology" type="date" value={calcDob} onChange={(e)=>setCalcDob(e.target.value)} className="mt-4 w-full rounded-xl border border-slate-700 bg-slate-900 px-3 py-3 text-white"/>{lifePath !== null && <p className="mt-3 text-sm text-indigo-100">Life path number: <strong>{lifePath}</strong></p>}</section></div>
      <p className="text-xs text-slate-500">Astrological and numerology traditions are interpretive systems, not evidence-based predictions. A missing or uncertain birth time affects the Ascendant and time-sensitive calculations.</p></div>;
  } else if (feature === 'Lagna & Chandra Charts') {
    const chart = chartMode === 'lagna' ? data.lagna_chart : data.chandra_chart;
    const chartData: VargaChartData | null = chart?.reference_sign_index == null ? null : {
      division: 1, name: chartMode === 'lagna' ? 'Lagna' : 'Chandra', brief: 'D1 · Whole-sign reference chart.',
      planets: Object.fromEntries(chart.planets.map((p: any) => [p.planet, p])),
      lagna_sign_index: chart.reference_sign_index, lagna_sign: chart.reference_sign, lagna_degree: null,
    };
    body = <><div className="mb-4 flex flex-wrap justify-between gap-2"><div className="flex gap-2">{(['lagna','chandra'] as const).map((mode) => <button key={mode} onClick={() => setChartMode(mode)} className={`rounded-lg px-3 py-2 text-sm ${chartMode===mode?'bg-indigo-600 text-white':'bg-slate-800 text-slate-300'}`}>{mode==='lagna'?'Lagna chart':'Chandra chart'}</button>)}</div><div className="flex gap-2">{(['north','south'] as const).map((style)=><button key={style} onClick={()=>setChartStyle(style)} className={`rounded-lg px-3 py-2 text-sm capitalize ${chartStyle===style?'bg-amber-500 text-slate-950':'bg-slate-800 text-slate-300'}`}>{style} Indian</button>)}</div></div>{chartData?<NatalChart data={chartData} style={chartStyle}/>:<ChartTable chart={chart}/>}</>;
  } else if (feature === 'Chalit Table & Chart') {
    const houses = data.chalit?.houses || [];
    body = data.chalit ? <><p className="mb-3 text-sm text-slate-400">{data.chalit.system}. House assignment changes by cusp; planetary sign longitudes remain unchanged.</p><div className="mx-auto mb-5 grid max-w-2xl grid-cols-3 gap-2">{houses.map((h:any)=><div key={h.house} className="min-h-20 rounded-xl border border-amber-200/30 bg-[#fff9ed] p-3 text-center text-slate-900"><div className="text-xs font-bold uppercase text-amber-800">Bhava {h.house}</div><div className="mt-2 text-sm font-semibold">{h.planets.join(' · ')||'—'}</div></div>)}</div><Table headers={['Bhava', 'Start cusp', 'Madhya', 'End cusp', 'Grahas']} rows={houses.map((h: any) => [h.house, `${h.start_cusp.toFixed(2)}°`, `${h.madhya.toFixed(2)}°`, `${h.end_cusp.toFixed(2)}°`, h.planets.join(', ') || '—'])} /></> : <p className="text-amber-200">Birth time required for bhava cusps.</p>;
  } else if (feature === 'Prastharashtakavarga Table') {
    const row = data.ashtakavarga?.rows?.[bavPlanet];
    body = data.ashtakavarga ? <><div className="mb-3 flex items-center gap-3"><label htmlFor="bav" className="text-sm text-slate-300">Recipient graha</label><select id="bav" value={bavPlanet} onChange={(e) => setBavPlanet(e.target.value)} className="rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-white">{Object.keys(data.ashtakavarga.rows).map((p: string) => <option key={p}>{p}</option>)}</select></div><p className="mb-3 text-xs text-slate-400">Each cell is a 0/1 bindu supplied by the contributor for that zodiac sign.</p><Table headers={['Sign', ...(row?.prastara || []).map((x: any) => x.contributor), 'BAV']} rows={data.ashtakavarga.signs.map((sign: string, i: number) => [sign, ...(row?.prastara || []).map((x: any) => x.bindus[i]), row?.bindus[i]])} /></> : <p className="text-amber-200">A reliable Lagna sign is required to calculate the Lagna contributor.</p>;
  } else if (feature === 'Ashtak Varga Table') {
    body = data.ashtakavarga ? <><Table headers={['Graha', ...data.ashtakavarga.signs, 'Total']} rows={[...Object.entries(data.ashtakavarga.rows).map(([p, r]: [string, any]) => [p, ...r.bindus, r.total]), ['Sarva', ...data.ashtakavarga.sarva, data.ashtakavarga.total]]} /><p className="mt-3 text-xs text-slate-400">{data.ashtakavarga.method} Checksum: {data.ashtakavarga.total} / {data.ashtakavarga.expected_total} raw bindus.</p></> : <p className="text-amber-200">A reliable birth time is needed for the Lagna bindu.</p>;
  } else if (feature === 'Aspect On Bhav Madhya') {
    body = data.bhava_aspects ? <><p className="mb-3 text-sm text-slate-400">Sign-based Parashari graha drishti to each Sripati bhava madhya; degree separation is shown for inspection.</p><Table headers={['House', 'Aspecting graha', 'Graha aspect', 'Separation']} rows={data.bhava_aspects.map((a: any) => [a.house, a.planet, a.aspect_label, `${a.separation_degrees}°`])} /></> : <p className="text-amber-200">Birth time required for bhava madhya.</p>;
  } else if (feature === 'Aspect On KP Cusp') {
    const cusps=data.kp?.cusps||[];
    body = data.kp ? <><p className="mb-3 text-sm text-slate-400">KP Krishnamurti cusps with star/sub-lords and sign-based graha aspects.</p><Table headers={['Cusp', 'Sign', 'Degree', 'Star lord', 'Sub lord', 'Aspected by']} rows={cusps.map((c: any) => [c.house,c.sign,`${c.degree.toFixed(2)}°`,c.star_lord,c.sub_lord,(data.kp.aspects_on_cusps||[]).filter((a:any)=>a.house===c.house).map((a:any)=>a.planet).join(', ')||'—'])} /></> : <p className="text-amber-200">Birth time required for KP cusps.</p>;
  } else if (feature === 'Shodashvarga Charts') {
    body = <div className="space-y-3 text-slate-300"><p>All 16 Parashari divisional charts are available in the Vedic Birth Charts section above.</p><a href="#vedic-charts" className="inline-block rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white">Go to Shodashvarga charts ↑</a></div>;
  } else if (feature === 'Friendship Table') {
    body = <><p className="mb-3 text-xs text-slate-400">Natural and temporary sign relationships combined into a five-fold label.</p><Table headers={['Graha', ...data.friendship.planets]} rows={data.friendship.matrix.map((r: any) => [r.planet,...r.relations.map((v:any)=>`${v.compound} (N:${v.natural}/T:${v.temporary})`)])} /></>;
  } else if (feature === 'Vimshottari Dasha') {
    const current=data.vimshottari?.current;
    body = <><p className="mb-3 text-sm text-indigo-200">Birth nakshatra: {data.vimshottari?.birth_nakshatra?.name} · current Mahadasha: {current?.lord || 'outside generated periods'}</p><Table headers={['Mahadasha', 'Start', 'End', 'Balance / years']} rows={rowsForPeriods(data.vimshottari?.periods).map((r: any[])=>[r[0],r[2],r[3],r[4]])} />{current?.antardashas?.length>0 && <div className="mt-4"><h4 className="mb-2 font-semibold text-indigo-200">Current Mahadasha Antardashas</h4><Table headers={['Antardasha lord','Start','End']} rows={current.antardashas.map((a:any)=>[a.lord,a.start,a.end])}/></div>}<p className="mt-3 text-xs text-slate-400">{data.vimshottari?.method}</p></>;
  } else if (feature === 'Shadbala & Bhavbala') {
    body = <><p className="mb-3 rounded-xl border border-amber-500/20 bg-amber-500/5 p-3 text-sm text-amber-100">{data.bala.status}</p><Table headers={['Graha','Uchcha component','Dig component','Naisargika']} rows={data.bala.planetary.map((p:any)=>[p.planet,`${p.uchcha_bala} virupas`,p.dig_bala==null?'—':`${p.dig_bala} virupas`,`${p.naisargika_bala} virupas`])}/><h4 className="mb-2 mt-5 font-semibold text-indigo-200">Bhava occupancy indicators</h4><Table headers={['Bhava','Madhya','Occupants','Count']} rows={data.bala.bhava.map((b:any)=>[b.house,`${b.madhya}°`,b.occupants.join(', ')||'—',b.occupant_count])}/><p className="mt-3 text-xs text-slate-500">{data.bala.method}</p></>;
  } else if (feature === 'Char Dasha') {
    body = data.char_dasha ? <><p className="mb-3 text-sm text-indigo-200">Current sign period: {data.char_dasha.current?.sign || 'not in generated range'} · {data.char_dasha.current?.lord || ''}</p><Table headers={['Sign period','Dasha lord','Start','End','Years']} rows={rowsForPeriods(data.char_dasha.periods)}/><p className="mt-3 text-xs text-slate-400">{data.char_dasha.method}</p></> : <p className="text-amber-200">A reliable birth time is required for Chara Dasha.</p>;
  } else if (feature === 'Yogini Dasha') {
    body = <><p className="mb-3 text-sm text-indigo-200">Birth Nakshatra: {data.yogini?.birth_nakshatra?.name} · Current: {data.yogini?.current?.yogini || 'not in generated range'}</p><Table headers={['Yogini','Graha','Start','End','Years']} rows={data.yogini.periods.map((p:any)=>[p.yogini,p.lord,p.start,p.end,p.years])}/><p className="mt-3 text-xs text-slate-400">{data.yogini.method}</p></>;
  } else if (feature === 'Western System') {
    body = <><p className="mb-3 text-sm text-slate-400">{data.western.method} This is shown separately from the Vedic sidereal charts.</p><Table headers={['Planet','Tropical sign','Degree','Motion']} rows={Object.entries(data.western.planets).map(([p,v]:[string,any])=>[p,v.sign,`${v.degree.toFixed(2)}°`,v.speed<0?'Retrograde':'Direct'])}/><div className="mt-4"><Table headers={['House cusp','Tropical longitude']} rows={data.western.houses.map((h:any)=>[h.house,`${h.cusp.toFixed(2)}°`])}/></div></>;
  } else if (feature === 'Print Sarvatobhadra Chakra') {
    body = <><div id="sbc-print-target"><p className="mb-3 text-sm text-slate-400">Moon’s birth Nakshatra: {data.sarvatobhadra.birth_nakshatra.name} · ★ marks the birth star.</p><div className="mx-auto grid max-w-2xl grid-cols-9 overflow-hidden rounded-xl border border-amber-200/40 bg-[#fff9ed]">{data.sarvatobhadra.grid.flat().map((cell:string,i:number)=><div key={i} className={`flex aspect-square items-center justify-center border border-amber-900/20 p-1 text-center text-[9px] text-amber-950 ${cell.startsWith('★')?'bg-amber-300 font-bold':''}`}>{cell}</div>)}</div><p className="mt-3 text-xs text-slate-500">{data.sarvatobhadra.method}</p></div><button type="button" onClick={()=>window.print()} className="mt-3 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white print:hidden">Print this chart</button></>;
  } else if (feature === 'Transit Today') {
    body = <><p className="mb-3 text-sm text-slate-400">Current Lahiri sidereal positions and close major aspects (3° orb) to natal grahas.</p><Table headers={['Graha','Sign','Degree','Motion']} rows={transitRows}/><h4 className="mb-2 mt-5 font-semibold text-indigo-200">Transit to natal aspects</h4><Table headers={['Transit graha','Aspect','Natal graha','Orb']} rows={data.transits.aspects.map((a:any)=>[a.transiting,a.aspect,a.natal,`${a.orb}°`])}/></>;
  } else if (feature === 'Dosha & Sade Sati Checks') {
    const checks = data.doshas;
    body = checks ? <div className="grid gap-4 lg:grid-cols-3">{[
      { title: 'Mangal Dosha screening', status: Object.values(checks.mangal_dosha.present_by_reference).some(Boolean) ? 'Flagged by at least one reference' : 'Not flagged by the displayed references', detail: `Mars houses — Lagna: ${checks.mangal_dosha.mars_houses.Lagna ?? 'birth time required'}, Moon: ${checks.mangal_dosha.mars_houses.Moon}, Venus: ${checks.mangal_dosha.mars_houses.Venus}. Houses checked: ${checks.mangal_dosha.trigger_houses.join(', ')}.`, method: checks.mangal_dosha.method },
      { title: 'Kaal Sarpa screening', status: checks.kaal_sarpa.present_by_strict_half_chart_rule ? 'Strict half-chart rule is met' : 'Strict half-chart rule is not met', detail: 'Checks whether all seven classical planets fall within one semicircle bounded by Rahu and Ketu.', method: checks.kaal_sarpa.method },
      { title: 'Sade Sati transit check', status: checks.sade_sati.active ? `Active · ${checks.sade_sati.phase}` : 'Not active by the displayed sign rule', detail: `Natal Moon: ${checks.sade_sati.natal_moon_sign}; transiting Saturn: ${checks.sade_sati.transit_saturn_sign}.`, method: checks.sade_sati.method },
    ].map((item) => <article key={item.title} className="rounded-2xl border border-indigo-300/15 bg-slate-900/70 p-4"><h3 className="font-semibold text-indigo-100">{item.title}</h3><p className="mt-2 text-sm font-medium text-amber-100">{item.status}</p><p className="mt-2 text-sm leading-relaxed text-slate-300">{item.detail}</p><p className="mt-3 border-t border-slate-700 pt-3 text-xs leading-relaxed text-slate-500">{item.method}</p></article>)}</div> : <p className="text-amber-200">Dosha calculations are not present in this backend response. Restart the updated backend and refresh.</p>;
  } else if (feature === 'Lal Kitab Chart & Planets Houses') {
    body = data.lal_kitab.houses.length ? <><p className="mb-3 text-sm text-slate-400">{data.lal_kitab.method}</p><Table headers={['Lal Kitab house','Sign','Planets']} rows={data.lal_kitab.houses.map((h:any)=>[h.house,h.sign,h.planets.join(', ')||'—'])}/></> : <p className="text-amber-200">{data.lal_kitab.notice}</p>;
  }

  return <section className="rounded-3xl border border-slate-700 bg-slate-800/95 p-6 shadow-xl">
    <div className="mb-4"><p className="text-xs font-semibold uppercase tracking-[0.2em] text-indigo-300">{t('Astrology tools')}</p><h2 className="mt-1 text-2xl font-semibold text-white">{t('Classical chart systems')}</h2><p className="mt-1 text-sm text-slate-400">{t('Choose a table or chart system. Calculation conventions are shown with each result.')}</p></div>
    <div className="mb-5 flex gap-2 overflow-x-auto pb-3" role="tablist" aria-label={t('Astrology features')}>{features.map((f)=><button key={f} role="tab" aria-selected={f===feature} onClick={()=>setFeature(f)} className={`shrink-0 rounded-full border px-4 py-2 text-sm ${f===feature?'border-indigo-400 bg-indigo-600 text-white':'border-slate-600 bg-slate-900 text-slate-300 hover:text-white'}`}>{t(f)}</button>)}</div>
    <div className="min-h-40">{body}</div>
    {data.method?.unknown_time && <p className="mt-4 rounded-lg border border-amber-500/20 bg-amber-500/5 p-3 text-xs text-amber-100">{data.method.unknown_time}</p>}
  </section>;
}
