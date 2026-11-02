'use client';

import React, { useEffect, useMemo, useRef, useState } from 'react';
import api from '@/lib/api';
import { useRouter } from 'next/navigation';
import tzLookup from '@photostructure/tz-lookup';
import { useLanguage } from '@/lib/i18n';

type PlaceFeature = {
  geometry?: { coordinates?: [number, number] };
  properties?: { name?: string; city?: string; state?: string; country?: string; district?: string; county?: string };
};

const inputClass = 'form-control w-full p-3 mt-1 bg-slate-700/90 border border-slate-600 rounded-lg outline-none focus:ring-2 focus:ring-indigo-500';

export default function OnboardingPage() {
  const { t, language } = useLanguage();
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [profile, setProfile] = useState({ full_name: '', gender: '', language_preference: 'en', preferred_system: 'both' });
  const [birth, setBirth] = useState({ label: 'Me', dob: '', tob: '', tob_unknown: false, birth_city: '', latitude: '', longitude: '', timezone: '' });
  const [placeQuery, setPlaceQuery] = useState('');
  const [places, setPlaces] = useState<PlaceFeature[]>([]);
  const [placeLoading, setPlaceLoading] = useState(false);
  const [placeError, setPlaceError] = useState('');
  const [placeOpen, setPlaceOpen] = useState(false);
  const [timeError, setTimeError] = useState('');
  const [timeHour, setTimeHour] = useState('');
  const [timeMinute, setTimeMinute] = useState('');
  const [timePeriod, setTimePeriod] = useState('AM');
  const placeBox = useRef<HTMLDivElement>(null);
  const placeSelected = useRef(false);

  useEffect(() => {
    setProfile((current) => ({ ...current, language_preference: language }));
  }, [language]);

  useEffect(() => {
    const value = birth.tob;
    if (!value) return;
    const [rawHour, minute] = value.split(':');
    const hour = Number(rawHour);
    setTimeHour(String(hour % 12 || 12).padStart(2, '0'));
    setTimeMinute(minute || '00');
    setTimePeriod(hour >= 12 ? 'PM' : 'AM');
  }, [birth.tob]);

  useEffect(() => {
    const query = placeQuery.trim();
    if (placeSelected.current || query.length < 2) { setPlaces([]); setPlaceLoading(false); return; }
    const controller = new AbortController();
    const timer = window.setTimeout(async () => {
      setPlaceLoading(true); setPlaceError('');
      try {
        const response = await fetch(`https://photon.komoot.io/api/?q=${encodeURIComponent(query)}&limit=7&lang=en`, { signal: controller.signal });
        if (!response.ok) throw new Error('Location search is temporarily unavailable.');
        const data = await response.json();
        setPlaces(Array.isArray(data.features) ? data.features : []);
      } catch (error) {
        if (!controller.signal.aborted) { setPlaces([]); setPlaceError('Could not search places. Check your connection and try again.'); }
      } finally { if (!controller.signal.aborted) setPlaceLoading(false); }
    }, 350);
    return () => { window.clearTimeout(timer); controller.abort(); };
  }, [placeQuery]);

  useEffect(() => {
    const close = (event: MouseEvent) => { if (!placeBox.current?.contains(event.target as Node)) setPlaceOpen(false); };
    document.addEventListener('mousedown', close);
    return () => document.removeEventListener('mousedown', close);
  }, []);

  const updateTime = (hour: string, minute: string, period: string) => {
    setTimeHour(hour); setTimeMinute(minute); setTimePeriod(period); setTimeError('');
    if (!hour || !minute || !period) { setBirth((current) => ({ ...current, tob: '' })); return; }
    const hour24 = (Number(hour) % 12) + (period === 'PM' ? 12 : 0);
    setBirth((current) => ({ ...current, tob: `${String(hour24).padStart(2, '0')}:${minute}` }));
  };

  const choosePlace = (feature: PlaceFeature) => {
    const p = feature.properties || {};
    const coordinates = feature.geometry?.coordinates;
    if (!coordinates || coordinates.length < 2) return;
    const [longitude, latitude] = coordinates;
    const city = p.city || p.name || p.district || p.county || '';
    const label = [city, p.state, p.country].filter(Boolean).filter((value, index, array) => array.indexOf(value) === index).join(', ');
    placeSelected.current = true;
    setPlaceQuery(label); setPlaces([]); setPlaceOpen(false); setPlaceError('');
    setBirth((current) => ({ ...current, birth_city: label, latitude: String(latitude), longitude: String(longitude), timezone: tzLookup(latitude, longitude) }));
  };

  const handleOnboard = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!birth.tob && !birth.tob_unknown) { setTimeError('Choose an hour, minute, and AM/PM, or mark the time unknown.'); return; }
    if (!birth.latitude || !birth.longitude || !birth.timezone) { setPlaceError('Choose a place from the suggestions so we can set its coordinates and timezone.'); return; }
    setLoading(true);
    try {
      await api.post('/profile/onboard', { profile_data: profile, birth_data: { ...birth, tob: birth.tob_unknown ? '12:00:00' : birth.tob, latitude: Number(birth.latitude), longitude: Number(birth.longitude) } });
      alert('Cosmic profile created! Welcome to AstroVerse.'); router.push('/dashboard');
    } catch (error: any) {
      if (error.response?.status === 401) {
        // Clear stale tokens (for example, after the local database or secret changes)
        // so the user can sign in again and receive a token for the active backend.
        localStorage.removeItem('token');
        alert('Your login session is no longer valid. Please log in again, then submit your birth details.');
        router.replace('/auth/login');
        return;
      }
      alert(error.response?.data?.detail || 'Onboarding failed');
    }
    finally { setLoading(false); }
  };

  const placeOptions = useMemo(() => places.map((feature) => {
    const p = feature.properties || {};
    const title = p.name || p.city || p.district || p.county || 'Unknown place';
    const detail = [p.city && p.city !== title ? p.city : '', p.state, p.country].filter(Boolean).filter((value, index, array) => array.indexOf(value) === index).join(', ');
    return { feature, title, detail };
  }), [places]);

  return (
    <main className="onboarding-shell min-h-screen text-white p-6 md:p-10">
      <div className="max-w-3xl mx-auto space-y-8">
        <header className="text-center"><h1 className="text-4xl font-bold text-indigo-400">{t('Create Your Cosmic Identity')}</h1><p className="text-slate-300 mt-2">{t('We need your exact birth details to calculate your stars.')}</p></header>
        <form onSubmit={handleOnboard} className="space-y-8">
          <section className="onboarding-panel p-6 bg-slate-800/85 backdrop-blur-md rounded-xl border border-slate-600/80 space-y-4">
            <h2 className="text-xl font-semibold text-indigo-300">1. {t('Personal Details')}</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div><label className="block text-sm text-slate-300">{t('Full Name')}</label><input type="text" value={profile.full_name} onChange={(e) => setProfile({ ...profile, full_name: e.target.value })} className={inputClass} required /></div>
              <div><label htmlFor="gender" className="block text-sm text-slate-300">{t('Gender')}</label><select id="gender" value={profile.gender} onChange={(e) => setProfile({ ...profile, gender: e.target.value })} className={inputClass}><option value="">{t('Select an option')}</option><option value="male">{t('Male')}</option><option value="female">{t('Female')}</option><option value="other">{t('Other gender')}</option></select></div>
            </div>
          </section>
          <section className="onboarding-panel p-6 bg-slate-800/85 backdrop-blur-md rounded-xl border border-slate-600/80 space-y-4">
            <h2 className="text-xl font-semibold text-indigo-300">2. {t('Birth Data')}</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
              <div><label className="block text-sm text-slate-300">{t('Date of Birth')}</label><input type="date" value={birth.dob} onChange={(e) => setBirth({ ...birth, dob: e.target.value })} className={inputClass} required /></div>
              <fieldset disabled={birth.tob_unknown} className="min-w-0"><legend className="block text-sm text-slate-300 mb-1">{t('Time of Birth')} <span aria-hidden="true">◷</span></legend><div className="flex items-center gap-2 rounded-lg border border-slate-600 bg-slate-700/90 p-2 focus-within:ring-2 focus-within:ring-indigo-500"><select aria-label="Hour" value={timeHour} onChange={(e) => updateTime(e.target.value, timeMinute, timePeriod)} className="min-w-0 flex-1 bg-transparent p-1 text-white outline-none"><option value="">HH</option>{Array.from({ length: 12 }, (_, i) => String(i + 1).padStart(2, '0')).map((h) => <option key={h} value={h}>{h}</option>)}</select><span>:</span><select aria-label="Minute" value={timeMinute} onChange={(e) => updateTime(timeHour, e.target.value, timePeriod)} className="min-w-0 flex-1 bg-transparent p-1 text-white outline-none"><option value="">MM</option>{Array.from({ length: 60 }, (_, i) => String(i).padStart(2, '0')).map((m) => <option key={m} value={m}>{m}</option>)}</select><select aria-label="AM or PM" value={timePeriod} onChange={(e) => updateTime(timeHour, timeMinute, e.target.value)} className="bg-transparent p-1 text-white outline-none"><option>AM</option><option>PM</option></select></div>{timeError && <p className="mt-1 text-sm text-rose-300" role="alert">{timeError}</p>}</fieldset>
              <label className="flex items-center gap-2 pb-3 text-sm text-slate-300"><input type="checkbox" checked={birth.tob_unknown} onChange={(e) => { setBirth({ ...birth, tob_unknown: e.target.checked }); setTimeError(''); }} className="w-5 h-5 rounded border-slate-600 text-indigo-600 bg-slate-700" />{t('Birth time unknown')}</label>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
              <div className="relative" ref={placeBox}>
                <label htmlFor="birth-city" className="block text-sm text-slate-300">{t('Birth City')}</label>
                <input id="birth-city" type="search" autoComplete="off" role="combobox" aria-expanded={placeOpen && placeOptions.length > 0} aria-controls="place-options" value={placeQuery} onFocus={() => setPlaceOpen(true)} onChange={(e) => { const value = e.target.value; placeSelected.current = false; setPlaceQuery(value); setBirth((current) => ({ ...current, birth_city: value, latitude: '', longitude: '', timezone: '' })); setPlaceOpen(true); }} className={inputClass} placeholder="Start typing a city, e.g. New Delhi" required />
                {placeOpen && (placeLoading || placeError || placeOptions.length > 0 || placeQuery.trim().length >= 2) && <div id="place-options" role="listbox" className="absolute z-20 mt-1 max-h-64 w-full overflow-auto rounded-lg border border-slate-600 bg-slate-900 shadow-2xl">{placeLoading && <p className="px-4 py-3 text-sm text-slate-300">{t('Searching places…')}</p>}{placeError && <p className="px-4 py-3 text-sm text-amber-200">{placeError}</p>}{!placeLoading && !placeError && placeOptions.length === 0 && <p className="px-4 py-3 text-sm text-slate-400">{t('No matching places found.')}</p>}{placeOptions.map(({ feature, title, detail }, index) => <button key={`${title}-${detail}-${index}`} type="button" role="option" aria-selected="false" onClick={() => choosePlace(feature)} className="block w-full border-b border-slate-700 px-4 py-3 text-left last:border-0 hover:bg-indigo-950 focus:bg-indigo-950 focus:outline-none"><span className="block font-medium text-white">{title}</span><span className="block text-sm text-slate-400">{detail}</span></button>)}<p className="px-4 py-2 text-xs text-slate-500">Search by OpenStreetMap via Photon</p></div>}
              </div>
              <div><label htmlFor="timezone" className="block text-sm text-slate-300">{t('Timezone')}</label><input id="timezone" type="text" value={birth.timezone} readOnly className={`${inputClass} read-only:cursor-not-allowed read-only:opacity-80`} placeholder="Automatically set from selected city" required /><p className="mt-1 text-xs text-slate-400">{t('Choose a city suggestion to fill this automatically.')}</p></div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
              <div><label className="block text-sm text-slate-300">Latitude</label><input type="number" step="any" min="-90" max="90" value={birth.latitude} readOnly className={`${inputClass} read-only:cursor-not-allowed read-only:opacity-80`} required /></div>
              <div><label className="block text-sm text-slate-300">Longitude</label><input type="number" step="any" min="-180" max="180" value={birth.longitude} readOnly className={`${inputClass} read-only:cursor-not-allowed read-only:opacity-80`} required /></div>
            </div>
          </section>
          <div className="flex justify-end"><button type="submit" disabled={loading} className="py-3 px-8 bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-600 transition-all rounded-lg font-bold text-lg shadow-lg">{loading ? t('Syncing with Stars...') : t('Complete Onboarding')}</button></div>
        </form>
      </div>
    </main>
  );
}
