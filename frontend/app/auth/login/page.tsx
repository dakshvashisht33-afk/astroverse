'use client';

import React, { useState } from 'react';
import api, { getApiErrorMessage } from '@/lib/api';
import { useRouter } from 'next/navigation';
import { useLanguage } from '@/lib/i18n';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const router = useRouter();
  const { t } = useLanguage();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const credentials = new URLSearchParams({ username: email, password });
      const response = await api.post('/auth/login', credentials, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      });
      localStorage.setItem('token', response.data.access_token);
      router.push('/onboarding');
    } catch (error: unknown) {
      alert(getApiErrorMessage(error, 'Login failed'));
    }
  };

  return (
    <div className="auth-shell min-h-screen flex items-center justify-center text-white p-4">
      <div className="auth-panel max-w-md w-full space-y-8 p-8 bg-slate-800 rounded-xl shadow-2xl border border-slate-700">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-indigo-400">AstroVerse</h1>
          <p className="text-slate-400 mt-2">{t('Welcome back to the cosmos')}</p>
        </div>
        <form onSubmit={handleLogin} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-slate-300">{t('Email Address')}</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="form-control w-full p-3 mt-1 bg-slate-700 border border-slate-600 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-300">{t('Password')}</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="form-control w-full p-3 mt-1 bg-slate-700 border border-slate-600 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none"
              required
            />
          </div>
          <button type="submit" className="w-full py-3 px-4 bg-indigo-600 hover:bg-indigo-500 transition-colors rounded-lg font-semibold">
            {t('Login')}
          </button>
        </form>
        <p className="text-center text-sm text-slate-400">
          {t("Don't have an account?")} <a href="/auth/signup" className="text-indigo-400 hover:underline">{t('Sign Up')}</a>
        </p>
      </div>
    </div>
  );
}
