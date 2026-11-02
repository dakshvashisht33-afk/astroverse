'use client';

import Link from 'next/link';
import { useLanguage } from '@/lib/i18n';

function StarMark() {
  return <svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M12 2.8c1.1 4.4 3.8 7.1 8.2 8.2-4.4 1.1-7.1 3.8-8.2 8.2-1.1-4.4-3.8-7.1-8.2-8.2 4.4-1.1 7.1-3.8 8.2-8.2Z" stroke="currentColor" strokeWidth="1.35"/><circle cx="19.4" cy="4.6" r="1.15" fill="currentColor"/></svg>;
}

export default function HomePage() {
  const { t } = useLanguage();
  return <main className="home-page">
    <header className="home-header">
      <Link href="/" className="brand-lockup" aria-label="AstroVerse home">
        <span className="brand-mark"><StarMark /></span><span className="brand-name">AstroVerse</span>
      </Link>
      <nav className="home-nav" aria-label="Account navigation">
        <Link className="home-link" href="/auth/login">{t('Log in')}</Link>
        <Link className="home-link home-link-primary" href="/auth/signup">{t('Create account')}</Link>
      </nav>
    </header>
    <section className="home-hero">
      <div className="home-copy">
        <h1>{t('A thoughtful way to read')} <span>{t('your sky.')}</span></h1>
        <p>{t('Explore your Vedic birth chart, follow the rhythms of the day, and find clear context for the questions that matter to you.')}</p>
        <div className="home-actions">
          <Link className="home-action home-action-main" href="/auth/signup">{t('Begin with your birth chart')} <span aria-hidden="true" className="ml-3">→</span></Link>
          <Link className="home-action" href="/auth/login">{t('I have an account')}</Link>
        </div>
        <p className="home-note">{t('Astrology for reflection and self-understanding. Readings are interpretive, not guarantees.')}</p>
      </div>
      <div className="home-chart" aria-hidden="true">
        <div className="chart-orbit" /><div className="chart-orbit" />
        <div className="chart-sun"><StarMark /></div>
        <span className="chart-label chart-label-one">Lagna · your way forward</span>
        <span className="chart-label chart-label-two">Chandra · inner nature</span>
        <span className="chart-label chart-label-three">Graha · planetary influences</span>
      </div>
    </section>
    <footer className="home-footer"><span>{t('AstroVerse · Vedic astrology, made personal')}</span><span>{t('Built around your chart and place of birth')}</span></footer>
  </main>;
}
