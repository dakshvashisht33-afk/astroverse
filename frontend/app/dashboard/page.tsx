'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import api from '@/lib/api';
import NatalChart, { type ChartStyle, type VargaChartData } from '@/components/ui/NatalChart';
import AstrologySuite from '@/components/ui/AstrologySuite';
import CompatibilityTool from '@/components/ui/CompatibilityTool';
import { useLanguage } from '@/lib/i18n';

const vargaOptions = [
  { division: 1, label: 'D1 Rāśi' }, { division: 2, label: 'D2 Hora' }, { division: 3, label: 'D3 Drekkana' },
  { division: 4, label: 'D4 Chaturthamsa' }, { division: 7, label: 'D7 Saptamsa' }, { division: 9, label: 'D9 Navamsa' },
  { division: 10, label: 'D10 Dasamsa' }, { division: 12, label: 'D12 Dwadashamsa' }, { division: 16, label: 'D16 Shodashamsa' },
  { division: 20, label: 'D20 Vimsamsa' }, { division: 24, label: 'D24 Chaturvimsamsa' }, { division: 27, label: 'D27 Saptavimsamsa' },
  { division: 30, label: 'D30 Trimsamsa' }, { division: 40, label: 'D40 Khavedamsa' }, { division: 45, label: 'D45 Akshavedamsa' },
  { division: 60, label: 'D60 Shashtiamsa' },
];

const menuItems = [
  { id: 'overview', label: 'Overview', icon: 'spark' },
  { id: 'horoscope', label: 'Horoscope', icon: 'moon' },
  { id: 'charts', label: 'Birth Charts', icon: 'chart' },
  { id: 'tools', label: 'Astrology Tools', icon: 'compass' },
  { id: 'match', label: 'Compatibility', icon: 'heart' },
] as const;
type MenuView = typeof menuItems[number]['id'];

function LineIcon({ name, className = '' }: { name: string; className?: string }) {
  const paths: Record<string, React.ReactNode> = {
    spark: <><path d="M12 3.5c1.1 4.3 3.2 6.4 7.5 7.5-4.3 1.1-6.4 3.2-7.5 7.5-1.1-4.3-3.2-6.4-7.5-7.5 4.3-1.1 6.4-3.2 7.5-7.5Z"/><path d="M19.5 3v3M18 4.5h3"/></>,
    moon: <path d="M19.3 15.5A8 8 0 0 1 8.5 4.7 8.2 8.2 0 1 0 19.3 15.5Z"/>,
    chart: <><rect x="4" y="4" width="16" height="16" rx="2"/><path d="M4 10h16M10 4v16M10 10l10 10"/></>,
    compass: <><circle cx="12" cy="12" r="9"/><path d="m15.5 8.5-2.2 4.8-4.8 2.2 2.2-4.8 4.8-2.2Z"/></>,
    heart: <path d="M20.5 8.7c0 4.3-8.5 10-8.5 10s-8.5-5.7-8.5-10a4.5 4.5 0 0 1 8.5-2.1 4.5 4.5 0 0 1 8.5 2.1Z"/>,
    wallet: <><rect x="3" y="6" width="18" height="14" rx="2"/><path d="M3 9h18M16 14h2"/></>,
  };
  return <svg aria-hidden="true" className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">{paths[name] || paths.spark}</svg>;
}

function CosmicTimingPanel({ data }: { data: any }) {
  const { t } = useLanguage();
  return <section className="relative overflow-hidden rounded-3xl border border-indigo-400/20 bg-gradient-to-br from-indigo-950 via-slate-900 to-slate-800 p-6 shadow-xl shadow-indigo-950/40">
    <div className="pointer-events-none absolute -right-12 -top-14 h-40 w-40 rounded-full bg-indigo-500/15 blur-3xl" />
    <div className="relative">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div><p className="text-xs font-semibold uppercase tracking-[0.2em] text-indigo-300">{t('Panchang windows')}</p><h2 className="mt-1 text-2xl font-semibold text-white">{t('Cosmic Timing')}</h2><p className="mt-1 text-sm text-slate-400">{t('Traditional daily windows calculated for your local sky.')}</p></div>
        <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1.5 text-xs text-slate-300">{data?.date || t('Today')}</span>
      </div>
      <div className="mt-5 grid grid-cols-2 gap-3 rounded-2xl border border-white/10 bg-black/20 p-4 sm:max-w-md">
        <div><div className="text-[11px] uppercase tracking-wider text-slate-400">{t('Sunrise')}</div><div className="mt-1 font-semibold text-amber-200">{data?.solar_events?.sunrise || '—'}</div></div>
        <div className="text-right"><div className="text-[11px] uppercase tracking-wider text-slate-400">{t('Sunset')}</div><div className="mt-1 font-semibold text-orange-200">{data?.solar_events?.sunset || '—'}</div></div>
      </div>
      {data?.panchang && <div className="mt-4 grid grid-cols-2 gap-2 sm:grid-cols-5">{Object.entries({ Vāra: data.panchang.weekday, Tithi: data.panchang.tithi, Nakshatra: data.panchang.nakshatra, Yoga: data.panchang.yoga, Karana: data.panchang.karana }).map(([label, value]) => <div key={label} className="rounded-xl border border-white/10 bg-white/[0.04] p-3"><div className="text-[10px] font-semibold uppercase tracking-wider text-slate-500">{label}</div><div className="mt-1 text-sm font-medium text-indigo-100">{value as string}</div></div>)}</div>}
      <p className="mt-2 text-xs text-slate-400">{data?.timezone} · {data?.daylight_minutes} minutes of daylight · Swiss Ephemeris</p>
      <div className="mt-5 grid grid-cols-1 gap-3 sm:grid-cols-2">
        {data?.windows?.map((window: any) => <article key={window.name} className={`rounded-2xl border p-4 ${window.type === 'favorable' ? 'border-emerald-400/25 bg-emerald-400/[0.08]' : 'border-rose-400/20 bg-rose-400/[0.06]'}`}>
          <div className="flex items-start justify-between gap-2"><span className={`text-sm font-bold ${window.type === 'favorable' ? 'text-emerald-300' : 'text-rose-300'}`}>{window.name}</span><span className="whitespace-nowrap rounded-lg bg-black/20 px-2 py-1 text-[11px] font-medium text-slate-200">{window.start}–{window.end}</span></div>
          <p className="mt-2 text-xs leading-relaxed text-slate-300">{window.description}</p>
        </article>)}
      </div>
      {data?.choghadiya?.length > 0 && <details className="group mt-4 rounded-2xl border border-white/10 bg-black/15 p-4"><summary className="cursor-pointer list-none text-sm font-semibold text-indigo-200">View all 16 Choghadiya intervals <span className="float-right text-slate-500 group-open:rotate-180">⌄</span></summary><div className="mt-4 grid gap-4 md:grid-cols-2">{(['Day', 'Night'] as const).map((period) => <div key={period}><h3 className="mb-2 text-xs font-semibold uppercase tracking-wider text-slate-400">{period}</h3><div className="space-y-1.5">{data.choghadiya.filter((item: any) => item.period === period).map((item: any) => <div key={`${item.period}-${item.name}-${item.start}`} className="flex items-center justify-between gap-2 rounded-lg bg-white/[0.04] px-3 py-2"><span className={`text-xs font-semibold ${item.quality === 'favorable' ? 'text-emerald-300' : item.quality === 'mixed' ? 'text-amber-200' : 'text-rose-300'}`}>{item.name}{item.date_offset ? ' · next day' : ''}</span><span className="whitespace-nowrap text-[11px] text-slate-400">{item.start}–{item.end}</span></div>)}</div></div>)}</div></details>}
      <p className="mt-4 text-[11px] leading-relaxed text-slate-500">{data?.notice}</p>
    </div>
  </section>;
}

function HoroscopePage({ horoscope, period, onPeriodChange }: { horoscope: any; period: string; onPeriodChange: (period: string) => void }) {
  const { t } = useLanguage();
  const periods = [
    { value: 'daily', label: t('Daily'), hint: t('A focused look at today') },
    { value: 'tomorrow', label: t('Tomorrow'), hint: t('A preview of the next day') },
    { value: 'weekly', label: t('Weekly'), hint: t('Themes for the week ahead') },
    { value: 'monthly', label: t('Monthly'), hint: t('A month-by-month chart reading') },
    { value: 'yearly', label: t('Yearly'), hint: t('Twelve months in one report') },
  ];
  const selected = periods.find((item) => item.value === period);
  const topicIcons = ['heart', 'wallet', 'spark', 'moon', 'compass'];
  return <main className="space-y-6">
    <section className="relative overflow-hidden rounded-3xl border border-indigo-400/20 bg-gradient-to-br from-indigo-950/90 via-slate-900 to-fuchsia-950/30 p-6 shadow-xl sm:p-8">
      <div className="pointer-events-none absolute -right-10 -top-20 h-64 w-64 rounded-full bg-indigo-500/10 blur-3xl" />
      <div className="relative flex flex-col justify-between gap-6 lg:flex-row lg:items-end">
        <div><p className="text-xs font-semibold uppercase tracking-[0.22em] text-indigo-300">{t('Your birth chart · Current sidereal transits')}</p><h2 className="mt-2 text-3xl font-bold tracking-tight text-white sm:text-4xl">{t('Your Horoscope')}</h2><p className="mt-2 max-w-xl text-slate-300">{t('Personal themes for love, finance, career, wellbeing, and spirituality, grounded in your saved chart.')}</p></div>
        <div className="rounded-2xl border border-white/10 bg-black/20 px-4 py-3 text-sm text-slate-300"><span className="block text-[11px] uppercase tracking-wider text-slate-500">Reading period</span><span className="mt-1 block font-semibold text-indigo-200">{horoscope?.date_range || 'Calculating transits…'}</span></div>
      </div>
    </section>

    <section className="rounded-3xl border border-slate-700 bg-slate-800/90 p-4 shadow-lg sm:p-5">
      <div className="grid grid-cols-2 gap-2 md:grid-cols-5">
        {periods.map((item) => <button key={item.value} type="button" onClick={() => onPeriodChange(item.value)} aria-pressed={period === item.value} className={`rounded-2xl border p-3 text-left transition-all sm:p-4 ${period === item.value ? 'border-indigo-400/60 bg-indigo-500/15 shadow-lg shadow-indigo-950/30' : 'border-slate-700 bg-slate-900/70 hover:border-slate-500'}`}>
          <span className={`block font-semibold ${period === item.value ? 'text-indigo-200' : 'text-slate-200'}`}>{item.label}</span><span className="mt-1 hidden text-xs text-slate-500 sm:block">{item.hint}</span>
        </button>)}
      </div>
      <div className="mt-4 flex flex-wrap items-center justify-between gap-2 border-t border-slate-700 pt-4"><p className="text-sm text-slate-300">{selected?.hint}</p><p className="text-xs text-slate-500">Chart-based themes · {horoscope?.date_range || 'Updating…'}</p></div>
    </section>

    {period === 'yearly' ? <>
      {horoscope?.overview && <section className="rounded-3xl border border-indigo-400/20 bg-gradient-to-br from-indigo-950/70 to-slate-900 p-6 text-sm leading-relaxed text-slate-200 shadow-lg"><p className="mb-2 text-xs font-semibold uppercase tracking-wider text-indigo-300">Year overview</p>{horoscope.overview}</section>}
      {horoscope?.months?.length ? <section className="grid gap-4 md:grid-cols-2">{horoscope.months.map((month: any, index: number) => <article key={month.month} className="relative overflow-hidden rounded-3xl border border-slate-700 bg-slate-800/90 p-5 shadow-lg"><div className="mb-3 flex items-center justify-between gap-3"><div className="flex items-center gap-3"><span className="flex h-9 w-9 items-center justify-center rounded-xl bg-indigo-500/15 text-sm font-bold text-indigo-200">{String(index + 1).padStart(2, '0')}</span><h3 className="text-lg font-semibold text-indigo-100">{month.month}</h3></div><span className="text-xs text-slate-500">{month.word_count} words</span></div><p className="text-sm leading-7 text-slate-300">{month.content}</p></article>)}</section> : <LoadingReading />}
    </> : horoscope?.sections?.length ? <section className="grid gap-4 lg:grid-cols-2">{horoscope.sections.map((section: any, index: number) => <article key={section.topic} className="group rounded-3xl border border-slate-700 bg-gradient-to-br from-slate-800 to-slate-900/90 p-5 shadow-lg transition-all hover:border-indigo-400/30 sm:p-6">
      <div className="mb-4 flex items-center justify-between"><div className="flex items-center gap-3"><span className="flex h-11 w-11 items-center justify-center rounded-xl border border-indigo-300/10 bg-indigo-500/15 text-indigo-200"><LineIcon name={topicIcons[index]} className="h-5 w-5" /></span><div><h3 className="text-lg font-semibold text-indigo-100">{section.topic}</h3><p className="text-xs text-slate-400">Personal chart reading</p></div></div><span className="rounded-full border border-slate-700 bg-slate-900/80 px-2.5 py-1 text-[11px] text-slate-300">{section.word_count} words</span></div>
      <p className="text-sm leading-7 text-slate-300 sm:text-[15px]">{section.content}</p>
    </article>)}</section> : <LoadingReading />}

    {horoscope && <footer className="rounded-2xl border border-slate-800 bg-slate-950/60 px-4 py-3 text-xs leading-relaxed text-slate-500"><span>{horoscope.method}</span><br /><span>{horoscope.notice}</span></footer>}
  </main>;
}

function LoadingReading() {
  return <div className="rounded-3xl border border-slate-700 bg-slate-800/70 p-10 text-center text-slate-400"><div className="mx-auto mb-3 h-8 w-8 animate-spin rounded-full border-2 border-indigo-400/30 border-t-indigo-300" />Personalizing your reading from the birth chart and current transits…</div>;
}

export default function Dashboard() {
  const { t } = useLanguage();
  const [chartData, setChartData] = useState<any>(null);
  const [vargaCharts, setVargaCharts] = useState<Record<string, VargaChartData> | null>(null);
  const [selectedDivision, setSelectedDivision] = useState(1);
  const [chartStyle, setChartStyle] = useState<ChartStyle>('north');
  const [timingData, setTimingData] = useState<any>(null);
  const [horoscope, setHoroscope] = useState<any>(null);
  const [birthProfileId, setBirthProfileId] = useState<string | null>(null);
  const [birthProfile, setBirthProfile] = useState<any>(null);
  const [advancedData, setAdvancedData] = useState<any>(null);
  const [advancedError, setAdvancedError] = useState<string | null>(null);
  const [selectedPeriod, setSelectedPeriod] = useState('weekly');
  const [activeMenu, setActiveMenu] = useState<MenuView>('overview');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadAllCosmicData() {
      try {
        const profileRes = await api.get('/profile/birth-profiles');
        if (!profileRes.data || profileRes.data.length === 0) {
          setError('No birth profile found. Please complete onboarding.');
          setLoading(false);
          return;
        }
        const profileId = profileRes.data[0].id;
        setBirthProfileId(profileId);
        setBirthProfile(profileRes.data[0]);
        // Render the dashboard as soon as the account is identified. Chart,
        // timing, and varga calculations can take longer and should not hold
        // the entire page behind the initial loading screen.
        setLoading(false);
        const [chartRes, timingRes, vargaRes] = await Promise.allSettled([
          api.get(`/chart/natal/${profileId}`), api.get('/timing/daily'), api.get(`/varga/charts/${profileId}`),
        ]);
        if (chartRes.status === 'fulfilled') setChartData(chartRes.value.data);
        if (timingRes.status === 'fulfilled') setTimingData(timingRes.value.data);
        if (vargaRes.status === 'fulfilled') setVargaCharts(vargaRes.value.data.charts);
        if (vargaRes.status === 'rejected' && vargaRes.reason?.response?.status === 404) {
          setError('The running backend does not have the Vedic charts route yet. Restart it from this updated project using: uvicorn backend.main:app');
        }
        api.get(`/chart/advanced/${profileId}`).then((res) => setAdvancedData(res.data)).catch((err) => {
          console.error('Advanced chart calculations unavailable', err);
          setAdvancedError(err.response?.data?.detail || 'Advanced chart tools could not load. Restart the updated backend and refresh.');
        });
      } catch (err: any) {
        const requestPath = err.config?.url || '';
        if (err.response?.status === 404 && requestPath.includes('/varga/charts/')) {
          setError('The running backend does not have the Vedic charts route yet. Restart it from this updated project using: uvicorn backend.main:app');
        } else if (err.response?.status === 401) {
          localStorage.removeItem('token');
          window.location.assign('/auth/login');
          return;
        } else {
          const detail = err.response?.data?.detail;
          const networkMessage = err.code === 'ERR_NETWORK' || err.code === 'ECONNABORTED'
            ? 'Could not connect to the backend at 127.0.0.1:8000. Start the Python server, then refresh this page.'
            : 'Failed to load your birth profile. Please refresh and try again.';
          setError(typeof detail === 'string' ? `${detail}${requestPath ? ` (${requestPath})` : ''}` : networkMessage);
        }
      } finally {
        setLoading(false);
      }
    }
    loadAllCosmicData();
  }, []);

  useEffect(() => {
    async function updateHoroscope() {
      try {
        if (!birthProfileId) return;
        const res = await api.get(`/horoscope/personalized/${birthProfileId}/${selectedPeriod}`);
        setHoroscope(res.data);
      } catch (err) {
        console.error('Personalized horoscope update failed', err);
      }
    }
    updateHoroscope();
  }, [selectedPeriod, birthProfileId]);

  if (loading) return <div className="flex min-h-screen items-center justify-center text-xl text-indigo-300"><span className="mr-3 inline-block h-5 w-5 animate-spin rounded-full border-2 border-indigo-400/30 border-t-indigo-300" />{t('Loading your cosmic dashboard…')}</div>;
  if (error) return <div className="flex min-h-screen items-center justify-center p-4 text-center text-red-300"><div><p className="text-lg">{error}</p><a href="/onboarding" className="mt-4 block text-indigo-300 underline">{t('Return to Onboarding')}</a></div></div>;

  return <div className="dashboard-shell min-h-screen text-white">
    <div className="mx-auto max-w-7xl space-y-6 px-4 py-5 sm:px-6 sm:py-8">
      <header className="flex flex-wrap items-center justify-between gap-4 border-b border-white/10 pb-5">
        <div><div className="flex items-center gap-2"><LineIcon name="spark" className="h-6 w-6 text-indigo-300"/><h1 className="text-3xl font-bold tracking-tight text-indigo-100 sm:text-4xl">AstroVerse</h1></div><p className="mt-1 text-sm text-slate-300">{t('Your personal cosmic guide')}</p></div>
        <Link href="/astro-ai" className="rounded-xl bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white shadow-lg shadow-indigo-950/40 transition-all hover:bg-indigo-500">{t('Ask Astro AI')} <span aria-hidden="true">→</span></Link>
      </header>

      <nav aria-label="Main menu" className="sticky top-2 z-20 -mx-1 flex gap-2 overflow-x-auto rounded-2xl border border-white/10 bg-slate-950/90 p-2 shadow-xl shadow-black/20 backdrop-blur-xl">
        {menuItems.map((item) => <button key={item.id} type="button" aria-current={activeMenu === item.id ? 'page' : undefined} onClick={() => setActiveMenu(item.id)} className={`flex shrink-0 items-center gap-2 rounded-xl px-4 py-2.5 text-sm font-medium transition-all ${activeMenu === item.id ? 'bg-indigo-500/20 text-indigo-100 ring-1 ring-inset ring-indigo-300/30' : 'text-slate-300 hover:bg-white/5 hover:text-white'}`}><LineIcon name={item.icon} className="h-4 w-4" />{t(item.label)}</button>)}
      </nav>

      {activeMenu === 'overview' && <main className="space-y-6">
        <section className="flex flex-col justify-between gap-5 rounded-3xl border border-indigo-300/15 bg-gradient-to-r from-indigo-950/75 via-slate-900/95 to-fuchsia-950/30 p-6 shadow-xl sm:flex-row sm:items-center sm:p-8">
          <div><p className="text-xs font-semibold uppercase tracking-[0.22em] text-indigo-300">{t('Your dashboard')}</p><h2 className="mt-2 text-2xl font-bold text-white sm:text-3xl">{t('A clearer view of your sky')}</h2><p className="mt-2 max-w-xl text-sm leading-relaxed text-slate-300">{t('Explore your personal horoscope, birth charts, and traditional timing tools from one simple menu.')}</p></div>
          <button type="button" onClick={() => setActiveMenu('horoscope')} className="shrink-0 rounded-xl bg-indigo-600 px-5 py-3 text-sm font-semibold text-white shadow-lg shadow-indigo-950/40 transition hover:bg-indigo-500">{t('Open my horoscope')} <span aria-hidden="true">→</span></button>
        </section>
        <div className="grid gap-6 lg:grid-cols-[1.3fr_0.7fr]">
          <CosmicTimingPanel data={timingData} />
          <div className="space-y-4">
            <button onClick={() => setActiveMenu('horoscope')} className="group w-full rounded-3xl border border-indigo-300/20 bg-slate-900/85 p-5 text-left shadow-lg transition hover:-translate-y-0.5 hover:border-indigo-300/50"><div className="flex items-center justify-between"><span className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-500/15 text-indigo-200"><LineIcon name="moon" className="h-5 w-5"/></span><span className="text-slate-300 transition group-hover:translate-x-1 group-hover:text-indigo-200">→</span></div><h3 className="mt-4 text-lg font-semibold text-white">{t('Your Horoscope')}</h3><p className="mt-1 text-sm leading-relaxed text-slate-300">{t('Daily, weekly, monthly, and yearly readings organized by life area.')}</p></button>
            <button onClick={() => setActiveMenu('charts')} className="group w-full rounded-3xl border border-slate-700 bg-slate-900/85 p-5 text-left shadow-lg transition hover:-translate-y-0.5 hover:border-amber-200/40"><div className="flex items-center justify-between"><span className="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-300/10 text-amber-100"><LineIcon name="chart" className="h-5 w-5"/></span><span className="text-slate-300 transition group-hover:translate-x-1 group-hover:text-amber-100">→</span></div><h3 className="mt-4 text-lg font-semibold text-white">{t('Birth Charts')}</h3><p className="mt-1 text-sm leading-relaxed text-slate-300">{t('Open your Lagna chart and the 16 divisional charts.')}</p></button>
            <button onClick={() => setActiveMenu('tools')} className="group w-full rounded-3xl border border-slate-700 bg-slate-900/85 p-5 text-left shadow-lg transition hover:-translate-y-0.5 hover:border-emerald-300/40"><div className="flex items-center justify-between"><span className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-300/10 text-emerald-100"><LineIcon name="compass" className="h-5 w-5"/></span><span className="text-slate-300 transition group-hover:translate-x-1 group-hover:text-emerald-100">→</span></div><h3 className="mt-4 text-lg font-semibold text-white">{t('Astrology Tools')}</h3><p className="mt-1 text-sm leading-relaxed text-slate-300">{t('Dasha, Ashtakavarga, KP cusps, transits, and more.')}</p></button>
          </div>
        </div>
      </main>}

      {activeMenu === 'horoscope' && <HoroscopePage horoscope={horoscope} period={selectedPeriod} onPeriodChange={setSelectedPeriod} />}

      {activeMenu === 'charts' && <main className="space-y-5">
        <section className="flex flex-wrap items-center justify-between gap-4 rounded-3xl border border-amber-200/10 bg-slate-900/70 p-6"><div><p className="text-xs font-semibold uppercase tracking-[0.2em] text-amber-100/80">{t('Lahiri sidereal · Whole-sign houses')}</p><h2 className="mt-2 text-2xl font-bold text-white">{t('Your Birth Charts')}</h2><p className="mt-1 text-sm text-slate-400">{t('Choose a divisional chart and your preferred Indian chart style.')}</p></div><div className="flex gap-2 rounded-xl border border-slate-700 bg-slate-950 p-1"><button type="button" aria-pressed={chartStyle==='north'} onClick={()=>setChartStyle('north')} className={`rounded-lg px-3 py-2 text-sm ${chartStyle==='north'?'bg-indigo-600 text-white':'text-slate-300'}`}>{t('North Indian')}</button><button type="button" aria-pressed={chartStyle==='south'} onClick={()=>setChartStyle('south')} className={`rounded-lg px-3 py-2 text-sm ${chartStyle==='south'?'bg-indigo-600 text-white':'text-slate-300'}`}>{t('South Indian')}</button></div></section>
        <section id="vedic-charts" className="rounded-3xl border border-slate-700 bg-slate-800/95 p-5 shadow-xl sm:p-7">
          <div className="chart-tabs mb-5 flex gap-2 overflow-x-auto pb-3" role="tablist" aria-label="Select divisional chart">{vargaOptions.map(({division,label})=><button key={division} type="button" role="tab" aria-selected={selectedDivision===division} onClick={()=>setSelectedDivision(division)} className={`shrink-0 rounded-full border px-4 py-2 text-sm transition-colors ${selectedDivision===division?'border-indigo-400 bg-indigo-600 text-white':'border-slate-600 bg-slate-900 text-slate-300 hover:border-indigo-400 hover:text-white'}`}>{label}</button>)}</div>
          {vargaCharts?.[String(selectedDivision)] ? <NatalChart data={vargaCharts[String(selectedDivision)]} style={chartStyle} advancedData={advancedData}/> : <p className="py-12 text-center text-slate-400">Calculating your Vedic charts…</p>}
        </section>
      </main>}

      {activeMenu === 'tools' && <main className="space-y-4"><section className="rounded-3xl border border-slate-700 bg-slate-900/70 p-6"><p className="text-xs font-semibold uppercase tracking-[0.2em] text-emerald-200/80">Explore your chart</p><h2 className="mt-2 text-2xl font-bold text-white">Astrology Tools</h2><p className="mt-1 text-sm text-slate-400">Switch between classical chart calculations from the feature menu.</p></section><AstrologySuite data={advancedData} error={advancedError}/></main>}

      {activeMenu === 'match' && birthProfileId && <CompatibilityTool profileId={birthProfileId} ownName={birthProfile?.label || 'My birth profile'} />}

      <footer className="border-t border-white/5 pt-4 text-center text-xs text-slate-600">AstroVerse · Traditional astrology readings are interpretive and not guaranteed predictions.</footer>
    </div>
  </div>;
}
