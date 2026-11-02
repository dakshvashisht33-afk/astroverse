'use client';

import React, { useMemo } from 'react';
import { useLanguage } from '@/lib/i18n';

export interface VargaPlacement {
  longitude: number;
  sign: string;
  sign_index: number;
  degree: number;
  house: number | null;
  dignity: string;
}

export interface VargaChartData {
  division: number;
  name: string;
  brief: string;
  planets: Record<string, VargaPlacement>;
  lagna_sign_index: number | null;
  lagna_sign: string | null;
  lagna_degree: number | null;
}

export type ChartStyle = 'north' | 'south';

const signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'];
const abbreviations: Record<string, string> = { Sun: 'Su', Moon: 'Mo', Mars: 'Ma', Mercury: 'Me', Jupiter: 'Ju', Venus: 'Ve', Saturn: 'Sa', Rahu: 'Ra', Ketu: 'Ke' };
const northHouseCenters = [
  // Centroids of the 12 cells in a North Indian diamond chart, clockwise from Lagna.
  [200, 78], [110, 50], [50, 110], [78, 200], [50, 290], [110, 350],
  [200, 322], [290, 350], [350, 290], [322, 200], [350, 110], [290, 50],
];
const southSignCells: [number, number][] = [
  [0, 0], [1, 0], [2, 0], [3, 0], [3, 1], [3, 2],
  [3, 3], [2, 3], [1, 3], [0, 3], [0, 2], [0, 1],
];

const chartMarker = (dignity: string) => {
  if (dignity === 'Exalted' || dignity === 'Own sign') return '↑';
  if (dignity === 'Debilitated') return '↓';
  if (dignity === 'Friendly sign') return '↗';
  if (dignity === 'Enemy sign') return '!';
  return '·';
};

const houseThemes: Record<number, string> = {
  1: 'identity, vitality, and self-direction', 2: 'resources, speech, and family values',
  3: 'skills, communication, and sustained effort', 4: 'home, foundations, and inner steadiness',
  5: 'learning, creativity, and considered risks', 6: 'service, routines, and problem-solving',
  7: 'partnerships, agreements, and collaboration', 8: 'change, research, and shared resources',
  9: 'principles, mentors, and long-range learning', 10: 'career, contribution, and responsibility',
  11: 'networks, gains, and long-term aims', 12: 'rest, retreat, and behind-the-scenes work',
};

export default function NatalChart({ data, style, advancedData }: { data: VargaChartData; style: ChartStyle; advancedData?: any }) {
  const { t } = useLanguage();
  const assessments: Record<string, any> = Object.fromEntries((advancedData?.planet_insights || []).map((item: any) => [item.planet, item]));
  const vimshottari = advancedData?.vimshottari;
  const byHouse = useMemo(() => {
    const grouped: Record<number, Array<[string, VargaPlacement]>> = {};
    Object.entries(data.planets).forEach(([name, position]) => {
      if (position.house == null) return;
      (grouped[position.house] ||= []).push([name, position]);
    });
    return grouped;
  }, [data.planets]);

  const bySign = useMemo(() => {
    const grouped: Record<number, Array<[string, VargaPlacement]>> = {};
    Object.entries(data.planets).forEach(([name, position]) => {
      (grouped[position.sign_index] ||= []).push([name, position]);
    });
    return grouped;
  }, [data.planets]);

  const signAtHouse = (house: number) => data.lagna_sign_index == null ? null : (data.lagna_sign_index + house - 1) % 12;

  return (
    <div className="flex flex-col items-center">
      <div className="mb-4 text-center">
        <h3 className="text-2xl font-semibold text-indigo-200">D{data.division} · {data.name}</h3>
        <p className="mt-1 text-sm text-slate-400">{t(data.brief)} {t('Sidereal zodiac')} · {t('Lahiri ayanamsha')} · {t('Whole-sign houses')}.</p>
        {data.lagna_sign && <p className="mt-2 text-sm text-amber-200">{t('Lagna')}: {t(data.lagna_sign)}</p>}
      </div>
      {data.lagna_sign_index == null && <p className="mb-4 max-w-lg text-center text-sm text-amber-200">{t('The birth time is marked unknown, so the Ascendant and house placements cannot be calculated. Planet signs are shown without houses.')}</p>}

      <svg viewBox="0 0 400 400" className="w-full max-w-[500px] rounded-xl border border-amber-200/50 bg-[#fff9ed] text-slate-900 shadow-2xl" role="img" aria-label={`D${data.division} ${data.name} Vedic chart in ${style === 'north' ? 'North Indian' : 'South Indian'} style`}>
        {style === 'north' ? (
          <>
            <rect x="20" y="20" width="360" height="360" fill="none" stroke="#9a4d25" strokeWidth="2" />
            <path d="M20 20 L380 380 M380 20 L20 380 M200 20 L380 200 L200 380 L20 200 Z" fill="none" stroke="#9a4d25" strokeWidth="1.5" />
            {northHouseCenters.map(([x, y], index) => {
              const house = index + 1;
              const signIndex = signAtHouse(house);
              const placements = byHouse[house] || [];
              return <g key={`north-${house}`}>
                <text x={x} y={y - 8} textAnchor="middle" fontSize="13" fontWeight="700" fill="#9a4d25">{signIndex == null ? '—' : signIndex + 1}</text>
                {signIndex === data.lagna_sign_index && <text x={x} y={y + 5} textAnchor="middle" fontSize="8" fontWeight="700" fill="#c2410c">ASC</text>}
                {placements.length > 0 && <text x={x} y={y + (signIndex === data.lagna_sign_index ? 20 : 14)} textAnchor="middle" fontSize="11" fontWeight="700" fill="#312e81">{placements.map(([name, placement], pIndex) => <tspan key={name}>{pIndex ? ' ' : ''}{abbreviations[name] || name.slice(0, 2)}<tspan fill={placement.dignity === 'Exalted' || placement.dignity === 'Own sign' ? '#047857' : placement.dignity === 'Debilitated' ? '#be123c' : '#64748b'}>{chartMarker(placement.dignity)}</tspan></tspan>)}</text>}
              </g>;
            })}
          </>
        ) : (
          <>
            {Array.from({ length: 16 }, (_, index) => {
              const col = index % 4;
              const row = Math.floor(index / 4);
              const x = 20 + col * 90;
              const y = 20 + row * 90;
              const isOuter = row === 0 || row === 3 || col === 0 || col === 3;
              return isOuter && <rect key={`south-cell-${index}`} x={x} y={y} width="90" height="90" fill="none" stroke="#9a4d25" strokeWidth="1.5" />;
            })}
            <text x="200" y="185" textAnchor="middle" fontSize="16" fontWeight="700" fill="#7c2d12">D{data.division} · {data.name}</text>
            <text x="200" y="208" textAnchor="middle" fontSize="11" fill="#475569">Vedic sidereal chart</text>
            <text x="200" y="229" textAnchor="middle" fontSize="10" fill="#475569">Lahiri · Whole sign</text>
            {southSignCells.map(([col, row], signIndex) => {
              const x = 65 + col * 90;
              const y = 42 + row * 90;
              const placements = bySign[signIndex] || [];
              const isLagna = signIndex === data.lagna_sign_index;
              const house = data.lagna_sign_index == null ? null : ((signIndex - data.lagna_sign_index + 12) % 12) + 1;
              const planetRows = [placements.slice(0, 4), placements.slice(4, 8), placements.slice(8, 12)];
              return <g key={`south-${signIndex}`}>
                <text x={x} y={y} textAnchor="middle" fontSize="12" fontWeight="700" fill="#9a4d25">{signIndex + 1}</text>
                <text x={x} y={y + 12} textAnchor="middle" fontSize="8" fontWeight={isLagna ? '700' : '400'} fill={isLagna ? '#c2410c' : '#64748b'}>{isLagna ? `ASC · H${house}` : house ? `H${house}` : signs[signIndex]}</text>
                {planetRows.map((group, rowIndex) => group.length > 0 && <text key={`planets-${rowIndex}`} x={x} y={y + 27 + rowIndex * 12} textAnchor="middle" fontSize="9" fontWeight="700" fill="#312e81">{group.map(([name, placement], pIndex) => <tspan key={name}>{pIndex ? ' ' : ''}{abbreviations[name] || name.slice(0, 2)}<tspan fill={placement.dignity === 'Exalted' || placement.dignity === 'Own sign' ? '#047857' : placement.dignity === 'Debilitated' ? '#be123c' : '#64748b'}>{chartMarker(placement.dignity)}</tspan></tspan>)}</text>)}
              </g>;
            })}
          </>
        )}
      </svg>

      <div className="mt-3 flex flex-wrap justify-center gap-x-4 gap-y-1 text-xs text-slate-400" aria-label={t('Planet condition markers')}><span><b className="text-emerald-300">↑</b> {t('exalted / own sign')}</span><span><b className="text-cyan-200">↗</b> {t('friendly sign')}</span><span><b className="text-rose-300">↓</b> {t('debilitated')}</span><span><b className="text-slate-300">! / ·</b> {t('enemy / neutral or unclassified')}</span></div>

      <div className="mt-6 w-full overflow-x-auto rounded-lg border border-slate-700 bg-slate-900">
        <table className="w-full min-w-[1250px] text-left text-sm">
          <thead className="bg-slate-800 text-xs uppercase text-slate-400"><tr><th className="px-3 py-3">{t('Graha')}</th><th className="px-3 py-3">{t('Sign')}</th><th className="px-3 py-3">{t('Degree')}</th><th className="px-3 py-3">{t('House')}</th><th className="px-3 py-3">{t('Sign dignity')}</th><th className="px-3 py-3">{t('Potential')}</th><th className="px-3 py-3">{t('House expression')}</th><th className="px-3 py-3">{t('Activation timing')}</th></tr></thead>
          <tbody className="divide-y divide-slate-800">{Object.entries(data.planets).map(([name, position]) => {
            const reading = data.division === 1 ? assessments[name] : null;
            const house = reading?.house ?? position.house;
            const dignityScore: Record<string, number> = { Exalted: 2, 'Own sign': 2, 'Friendly sign': 1, 'Neutral sign': 0, 'Enemy sign': -1, Debilitated: -2 };
            let fallbackScore = dignityScore[position.dignity] ?? 0;
            if (house != null) fallbackScore += [1, 5, 9, 10, 11].includes(house) ? 1 : [6, 8, 12].includes(house) ? -1 : 0;
            const fallbackPotential = house == null ? `${position.dignity} sign placement · house effects unavailable` : fallbackScore >= 2 ? 'Strong supportive placement signal' : fallbackScore >= 1 ? 'Supportive placement signal' : fallbackScore <= -2 ? 'More effort may be needed' : fallbackScore < 0 ? 'Mixed placement signal' : 'Context-dependent placement signal';
            const potentialFactors: string[] = reading?.potential_factors?.length ? reading.potential_factors : [position.dignity, house == null ? 'house unknown' : `whole-sign house ${house}`];
            const potentialText = reading?.potential && !/unavailable/i.test(reading.potential) ? reading.potential : fallbackPotential;
            const dashaPeriods = vimshottari?.periods || [];
            const currentAntardashas = vimshottari?.current?.antardashas || [];
            const activation = reading?.activation_periods?.length ? reading.activation_periods : [
              ...dashaPeriods.filter((period: any) => period.lord === name).map((period: any) => ({ ...period, period: 'Mahadasha' })),
              ...currentAntardashas.filter((period: any) => period.lord === name).map((period: any) => ({ ...period, period: 'Current Mahadasha · Antardasha' })),
            ];
            const activationText = activation.length
              ? <>{advancedData?.time_unknown && <span className="mb-1 block text-amber-200">Estimated dates · birth time marked unknown</span>}{activation.map((period: any) => <div key={`${period.period}-${period.start}`}><span className="font-medium text-amber-200">{period.period}</span>{period.status ? ` · ${period.status}` : ''} · {period.start} – {period.end}</div>)}</>
              : vimshottari ? 'No matching period in the calculated Vimshottari horizon.' : 'Vimshottari dates are not loaded yet. Restart the updated backend and refresh.';
            return <tr key={name} className="align-top"><td className="px-3 py-3 font-medium text-indigo-300">{name}</td><td className="px-3 py-3 text-slate-300">{t(position.sign)}</td><td className="px-3 py-3 text-slate-400">{position.degree.toFixed(2)}°</td><td className="px-3 py-3 text-slate-400">{house ?? '—'}</td><td className="px-3 py-3"><span className={`rounded-full px-2.5 py-1 text-xs font-semibold ${position.dignity === 'Exalted' ? 'bg-emerald-400/15 text-emerald-300' : position.dignity === 'Debilitated' ? 'bg-rose-400/15 text-rose-300' : position.dignity === 'Own sign' ? 'bg-indigo-400/15 text-indigo-200' : position.dignity === 'Friendly sign' ? 'bg-cyan-400/15 text-cyan-200' : 'bg-slate-700 text-slate-300'}`}>{t(position.dignity)}</span></td><td className="max-w-[210px] px-3 py-3 text-indigo-100"><span className="font-medium">{potentialText}</span><p className="mt-1 text-xs leading-relaxed text-slate-400">{t('Factors')}: {potentialFactors.map((factor: string) => t(factor)).join(' · ')}</p></td><td className="max-w-[300px] px-3 py-3 leading-relaxed text-slate-300">{reading?.insight || (house ? `${t(houseThemes[house])}. ${t(position.dignity)} ${t('sign dignity modifies how consistently these themes may be expressed.')}` : t('House themes require a known birth time.'))}</td><td className="max-w-[260px] px-3 py-3 text-xs leading-relaxed text-slate-400">{activationText}</td></tr>;
          })}</tbody>
        </table>
      </div>
      <p className="mt-2 w-full text-xs leading-relaxed text-slate-500">Potential is a qualitative screen based on sign dignity and house placement; where available, the backend also weighs lordship, conjunctions, and classical planetary aspects. Activation dates come from the calculated Vimshottari schedule and indicate periods to review, not guaranteed “best result” dates. Traditional strength judgments vary, and this is not a full Shadbala calculation.</p>

      {data.division === 1 && advancedData?.yogas && <section className="mt-7 w-full rounded-2xl border border-amber-200/15 bg-gradient-to-br from-amber-950/20 via-slate-900 to-indigo-950/20 p-5 sm:p-6">
        <div className="flex flex-wrap items-end justify-between gap-3"><div><p className="text-xs font-semibold uppercase tracking-[0.2em] text-amber-200/80">D1 · Rule-based screening</p><h3 className="mt-1 text-xl font-semibold text-amber-100">Yogas in your Kundali</h3></div><span className="text-xs text-slate-400">{advancedData.yogas.items?.length || 0} rule matches</span></div>
        <p className="mt-3 max-w-4xl text-sm leading-relaxed text-slate-300">A yoga is a chart combination to investigate, not a guaranteed outcome. Each match below shows its trigger and the factors that can strengthen, weaken, or change its expression.</p>
        {advancedData.yogas.available ? (advancedData.yogas.items?.length ? <div className="mt-4 grid gap-3 md:grid-cols-2">{advancedData.yogas.items.map((yoga: any, index: number) => <article key={`${yoga.name}-${index}`} className="rounded-xl border border-white/[0.08] bg-slate-950/40 p-4">
          <div className="flex flex-wrap items-center justify-between gap-2"><h4 className="font-semibold text-indigo-100">{yoga.name}</h4><span className="rounded-full bg-amber-200/10 px-2.5 py-1 text-[11px] text-amber-100">{yoga.category}</span></div>
          <p className="mt-2 text-xs font-medium text-emerald-200/90">{yoga.status || 'Rule matched · strength not graded'}</p>
          <p className="mt-2 text-xs leading-relaxed text-slate-400"><span className="font-semibold text-slate-300">Why it matched:</span> {yoga.basis}</p>
          {yoga.planets?.length > 0 && <p className="mt-2 text-xs text-slate-400"><span className="font-semibold text-slate-300">Planets:</span> {yoga.planets.join(', ')}{yoga.houses?.length ? ` · Houses: ${yoga.houses.join(', ')}` : ''}</p>}
          <p className="mt-2 text-sm leading-relaxed text-slate-300">{yoga.interpretation}</p>
          {yoga.modifiers_to_review?.length > 0 && <div className="mt-3 rounded-lg border border-white/[0.06] bg-white/[0.03] p-3"><p className="text-xs font-semibold text-amber-100">What can modify the result</p><ul className="mt-1 list-disc space-y-1 pl-4 text-xs leading-relaxed text-slate-400">{yoga.modifiers_to_review.map((modifier: string, modifierIndex: number) => <li key={`${modifierIndex}-${modifier}`}>{modifier}</li>)}</ul></div>}
          {yoga.classical_reference && <p className="mt-3 text-[11px] text-slate-500">Tradition reference: {yoga.classical_reference}</p>}
        </article>)}</div> : <p className="mt-4 rounded-xl bg-slate-950/40 p-4 text-sm text-slate-300">No supported yoga rules were matched in this D1 screening. That does not rule out combinations defined by other traditions or more detailed conditions.</p>) : <p className="mt-4 text-sm text-amber-100">{advancedData.yogas.method}</p>}
        <p className="mt-4 text-xs leading-relaxed text-slate-500">{advancedData.yogas.method}</p>
      </section>}
    </div>
  );
}
