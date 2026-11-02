import type { Metadata } from 'next';
import './globals.css';
import '@fontsource-variable/manrope';
import '@fontsource-variable/dm-sans';
import GalaxyBackground from '@/components/ui/GalaxyBackground';
import { LanguageProvider } from '@/lib/i18n';

export const metadata: Metadata = {
  title: 'AstroVerse',
  description: 'Astrology insights for entertainment and self-reflection.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <LanguageProvider>
        <GalaxyBackground />
        <div className="app-content">{children}</div>
        </LanguageProvider>
      </body>
    </html>
  );
}
