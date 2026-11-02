'use client';

import React, { useEffect, useRef, useState } from 'react';
import Link from 'next/link';
import api from '@/lib/api';
import { useLanguage } from '@/lib/i18n';

type ChatItem = { role: 'user' | 'assistant'; text: string; contextFactors?: string[] };
const suggestions = [
  'What stands out in my birth chart?',
  'How can I work with my current dasha?',
  'What chart factors shape my career?',
  'What should I understand about relationships?',
];

function AstroMark({ className = 'h-5 w-5' }: { className?: string }) {
  return <svg aria-hidden="true" className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round"><path d="M12 3.5c1.1 4.3 3.2 6.4 7.5 7.5-4.3 1.1-6.4 3.2-7.5 7.5-1.1-4.3-3.2-6.4-7.5-7.5 4.3-1.1 6.4-3.2 7.5-7.5Z"/><path d="M19.5 3v3M18 4.5h3" strokeLinecap="round"/></svg>;
}

function MoonMark({ className = 'h-5 w-5' }: { className?: string }) {
  return <svg aria-hidden="true" className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"><path d="M19 15.5A8 8 0 0 1 8.5 5 8.2 8.2 0 1 0 19 15.5Z"/></svg>;
}

function renderInline(text: string, keyPrefix: string) {
  return text.split(/(\*\*[^*]+\*\*)/g).map((part, index) =>
    part.startsWith('**') && part.endsWith('**')
      ? <strong key={`${keyPrefix}-${index}`} className="font-semibold text-indigo-100">{part.slice(2, -2)}</strong>
      : <React.Fragment key={`${keyPrefix}-${index}`}>{part.replace(/\*([^*]+)\*/g, '$1')}</React.Fragment>
  );
}

function FormattedReply({ text }: { text: string }) {
  const lines = text.split(/\r?\n/);
  return <div className="space-y-3 text-[15px] leading-7 text-slate-200">
    {lines.map((line, index) => {
      const value = line.trim();
      if (!value) return null;
      const heading = value.match(/^#{1,3}\s+(.+)/);
      if (heading) return <h3 key={index} className="pt-1 text-base font-semibold text-indigo-200">{renderInline(heading[1], `h-${index}`)}</h3>;
      const bullet = value.match(/^(?:[-*•])\s+(.+)/);
      if (bullet) return <div key={index} className="flex gap-3"><span className="mt-0.5 text-indigo-300" aria-hidden="true">·</span><p className="min-w-0 flex-1">{renderInline(bullet[1], `b-${index}`)}</p></div>;
      const numbered = value.match(/^\d+[.)]\s+(.+)/);
      if (numbered) return <div key={index} className="flex gap-3"><span className="mt-0.5 text-indigo-300" aria-hidden="true">{numbered[0].replace(/[.)]/g, '')}.</span><p className="min-w-0 flex-1">{renderInline(numbered[1], `n-${index}`)}</p></div>;
      return <p key={index}>{renderInline(value, `p-${index}`)}</p>;
    })}
  </div>;
}

export default function AIChat() {
  const { language, t } = useLanguage();
  const [messages, setMessages] = useState<ChatItem[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }, [messages, isLoading]);

  const handleSend = async (e?: React.FormEvent, prompt?: string) => {
    e?.preventDefault();
    const userMsg = (prompt ?? input).trim();
    if (!userMsg || isLoading) return;
    setInput('');
    setError('');
    setMessages((prev) => [...prev, { role: 'user', text: userMsg }]);
    setIsLoading(true);
    try {
      const history = messages.slice(-12).map(({ role, text }) => ({ role, text }));
      const res = await api.post('/ai/chat', { text: userMsg, history, response_language: language }, { timeout: 80000 });
      setMessages((prev) => [...prev, { role: 'assistant', text: res.data.response, contextFactors: res.data.context_factors || [] }]);
    } catch (err: any) {
      const networkFailure = err.code === 'ERR_NETWORK' || !err.response;
      setError(err.response?.data?.detail || (language === 'hi'
        ? networkFailure
          ? 'Astro AI सर्वर तक पहुँच नहीं पा रहा। जाँचें कि backend चल रहा है और frontend 3000 या 3001 पोर्ट पर खुला है। फिर backend को restart करें।'
          : 'Astro AI अभी जवाब नहीं दे पाया। कृपया थोड़ी देर बाद फिर कोशिश करें।'
        : networkFailure
          ? 'Astro AI cannot reach the backend. Make sure the Python server is running. If this page is on port 3001, restart the backend after the CORS update.'
          : 'Astro AI could not complete the response. Please try again shortly.'));
    } finally {
      setIsLoading(false);
    }
  };

  return <main className="ai-shell relative flex min-h-[100svh] flex-col overflow-hidden text-white">
    <div aria-hidden="true" className="pointer-events-none absolute inset-0 overflow-hidden">
      <div className="absolute -left-40 top-20 h-96 w-96 rounded-full bg-indigo-600/15 blur-[110px]" />
      <div className="absolute -right-40 bottom-10 h-[30rem] w-[30rem] rounded-full bg-fuchsia-600/10 blur-[130px]" />
      <div className="absolute left-1/2 top-1/3 h-72 w-72 -translate-x-1/2 rounded-full border border-indigo-400/[0.07]" />
    </div>
    <header className="relative z-10 flex items-center justify-between border-b border-white/[0.08] px-5 py-4 sm:px-10">
      <Link href="/dashboard" className="flex items-center gap-3 text-sm text-slate-300 transition hover:text-white"><span className="grid h-10 w-10 place-items-center rounded-xl border border-indigo-300/20 bg-indigo-400/10 text-indigo-200"><AstroMark /></span><span><span className="block font-semibold text-white">AstroVerse</span><span className="text-xs text-slate-400">{t('Your personal cosmic guide')}</span></span></Link>
      <div className="flex items-center gap-2 sm:gap-4"><span className="hidden items-center gap-2 rounded-full border border-emerald-300/15 bg-emerald-300/[0.06] px-3 py-1.5 text-xs text-emerald-100 sm:flex"><i className="h-1.5 w-1.5 rounded-full bg-emerald-300" />{t('Chart connected')}</span><Link href="/dashboard" className="rounded-xl border border-white/10 bg-white/[0.04] px-3 py-2 text-sm text-slate-300 hover:bg-white/[0.08]">{t('← Dashboard')}</Link></div>
    </header>

    <section className="relative z-10 mx-auto flex w-full max-w-[2400px] flex-1 flex-col px-3 py-3 sm:px-6 sm:py-4">
      <div className="mb-3 text-center sm:mb-4"><h1 className="text-3xl font-semibold tracking-tight text-white sm:text-4xl">Astro AI</h1><p className="mx-auto mt-1 max-w-xl text-sm leading-relaxed text-slate-300">{t('Thoughtful Vedic astrology insights, grounded in your saved birth chart and the question that matters to you.')}</p></div>

      <section aria-label="Astro AI conversation" className="mx-auto flex min-h-[calc(100svh-200px)] w-full flex-1 flex-col overflow-hidden rounded-[1.75rem] border border-indigo-200/10 bg-slate-900/75 shadow-[0_30px_100px_-35px_rgba(79,70,229,0.32)] backdrop-blur-xl">
        <div className="flex items-center justify-between border-b border-white/[0.08] bg-slate-800 px-5 py-4 sm:px-6"><div className="flex items-center gap-3"><span className="grid h-10 w-10 place-items-center rounded-xl bg-indigo-400/10 text-indigo-200"><MoonMark /></span><div><h2 className="font-semibold text-indigo-100">{t('Your chart companion')}</h2><p className="text-xs text-slate-300">{t('Private birth identifiers stay out of the AI request')}</p></div></div><button type="button" onClick={() => { setMessages([]); setError(''); }} className="rounded-lg px-3 py-2 text-xs text-slate-300 transition hover:bg-white/5 hover:text-white">{t('New chat')}</button></div>

        <div ref={scrollRef} className="flex-1 space-y-6 overflow-y-auto p-4 sm:p-7 lg:p-9">
          {!messages.length && <div className="flex min-h-[32vh] flex-col items-center justify-center py-8 text-center"><span className="mb-4 grid h-12 w-12 place-items-center rounded-full border border-indigo-200/30 text-indigo-200"><MoonMark className="h-6 w-6"/></span><h3 className="text-xl font-medium text-white">{t('What would you like to explore?')}</h3><p className="mt-2 max-w-md text-sm leading-relaxed text-slate-300">{t('Ask about a life area, a chart placement, or how your current planetary period may feel. I’ll explain the chart factors behind the reading.')}</p><div className="mt-6 grid w-full max-w-2xl gap-2 sm:grid-cols-2">{suggestions.map((suggestion) => <button key={suggestion} type="button" onClick={() => void handleSend(undefined, t(suggestion))} className="min-h-12 rounded-xl border border-white/[0.12] bg-white/[0.025] p-3 text-left text-sm text-slate-200 transition hover:border-indigo-300/40 hover:bg-indigo-400/[0.07] hover:text-white">{t(suggestion)}</button>)}</div></div>}
          {messages.map((message, index) => <div key={`${index}-${message.role}`} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}><article className={`max-w-[94%] rounded-2xl px-4 py-4 sm:px-6 sm:py-5 ${message.role === 'user' ? 'rounded-br-md border border-indigo-300/20 bg-gradient-to-br from-indigo-600 to-violet-700 text-white shadow-lg shadow-indigo-950/20 sm:max-w-[78%]' : 'w-full rounded-bl-md border border-white/[0.08] bg-slate-800/85 sm:max-w-6xl'}`}>
            {message.role === 'assistant' ? (<><div className="mb-2 flex items-center gap-2 text-xs font-semibold text-indigo-200"><AstroMark className="h-4 w-4"/> Astro AI</div><FormattedReply text={message.text} />{message.contextFactors?.length ? <details className="mt-4 border-t border-white/[0.08] pt-3"><summary className="cursor-pointer text-xs font-medium text-slate-300 hover:text-indigo-200">{t('Chart factors considered')}</summary><p className="mt-2 text-xs leading-relaxed text-slate-300">{message.contextFactors.join(' · ')}</p></details> : null}</>) : <p className="whitespace-pre-wrap text-[15px] leading-7">{message.text}</p>}
          </article></div>)}
          {isLoading && <div className="flex justify-start"><div className="flex items-center gap-3 rounded-2xl rounded-bl-md border border-white/[0.08] bg-slate-800/85 px-5 py-4 text-sm text-slate-300"><span className="flex gap-1"><i className="h-1.5 w-1.5 animate-bounce rounded-full bg-indigo-300"/><i className="h-1.5 w-1.5 animate-bounce rounded-full bg-indigo-300 [animation-delay:120ms]"/><i className="h-1.5 w-1.5 animate-bounce rounded-full bg-indigo-300 [animation-delay:240ms]"/></span>{t('Reading your chart…')}</div></div>}
          {error && <div role="alert" className="mx-auto max-w-xl rounded-xl border border-rose-300/15 bg-rose-400/[0.06] px-4 py-3 text-sm text-rose-200">{error}<button type="button" onClick={() => void handleSend(undefined, messages.at(-1)?.role === 'user' ? messages.at(-1)?.text : input)} className="ml-3 underline underline-offset-2">Try again</button></div>}
        </div>

        <form onSubmit={(event) => void handleSend(event)} className="border-t border-white/[0.08] bg-slate-950/60 p-3 sm:p-4"><div className="flex items-end gap-2 rounded-2xl border border-white/10 bg-slate-800/80 p-2 transition focus-within:border-indigo-400/50 focus-within:ring-2 focus-within:ring-indigo-500/15"><textarea value={input} onChange={(event) => setInput(event.target.value)} onKeyDown={(event) => { if (event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); void handleSend(); } }} rows={1} placeholder={t('Ask about your stars…')} aria-label={t('Your question')} className="max-h-36 min-h-11 flex-1 resize-y bg-transparent px-3 py-2.5 text-sm text-white outline-none placeholder:text-slate-500"/><button type="submit" disabled={isLoading || !input.trim()} className="rounded-xl bg-indigo-500 px-5 py-3 text-sm font-semibold text-white shadow-lg shadow-indigo-950/40 transition hover:bg-indigo-400 disabled:cursor-not-allowed disabled:opacity-40">{isLoading ? '…' : t('Ask')}<span className="ml-2" aria-hidden="true">↑</span></button></div><p className="mt-2 text-center text-[11px] text-slate-600">{t('Astrology is for reflection and insight, not a guarantee of future events.')}</p></form>
      </section>
    </section>
  </main>;
}
