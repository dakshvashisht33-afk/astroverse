'use client';

import React, { useState } from 'react';
import api from '@/lib/api';
import { useLanguage } from '@/lib/i18n';

export default function PricingPage() {
  const { t } = useLanguage();
  const [selectedPlan, setSelectedPlan] = useState('plus');
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  const plans = [
    {
      id: 'free',
      name: 'Cosmic Free',
      price: '0',
      description: 'Basic insights for casual explorers',
      features: ['Daily Horoscope', 'Basic Natal Chart', '5 AI Messages/Month', 'Standard Support'],
      buttonText: 'Current Plan',
      color: 'bg-slate-800',
      borderColor: 'border-slate-700'
    },
    {
      id: 'plus',
      name: 'Astral Plus',
      price: '9.99',
      description: 'Deep dive into your destiny',
      features: ['All Free Features', '100 AI Messages/Month', 'Premium PDF Reports', 'Priority Support', 'Ad-Free Experience'],
      buttonText: 'Choose Plus',
      color: 'bg-indigo-900/40',
      borderColor: 'border-indigo-500',
      popular: true
    },
    {
      id: 'pro',
      name: 'Galactic Pro',
      price: '29.99',
      description: 'Professional grade astrological tools',
      features: ['All Plus Features', 'Unlimited AI Messages', 'Full D1-D60 Analysis', '1-on-1 Consultant Access', 'Custom API Access'],
      buttonText: 'Choose Pro',
      color: 'bg-slate-800',
      borderColor: 'border-slate-700'
    }
  ];

  const handleUpgrade = async () => {
    setLoading(true);
    setErrorMessage('');
    try {
      // Step 1: Request a checkout session from our backend
      const res = await api.post('/payments/create-checkout-session', {
        plan_id: selectedPlan,
        provider: 'stripe' // Defaulting to stripe for this demo
      });

      // Step 2: Redirect user to the payment gateway
      window.location.href = res.data.checkout_url;
    } catch (error: any) {
      setErrorMessage(error.response?.data?.detail || 'Payment initiation failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900/35 text-white p-6">
      <div className="max-w-6xl mx-auto space-y-12 py-12">
        <div className="text-center space-y-4">
          <h1 className="text-5xl font-bold text-indigo-400 tracking-tight">{t('Unlock Your Destiny')}</h1>
          <p className="text-slate-400 text-lg max-w-2xl mx-auto">
            {t('Choose the plan that fits your journey. From casual curiosity to professional mastery.')}
          </p>
        </div>

        <div className="rounded-xl border border-amber-500/40 bg-amber-950/30 p-4 text-center text-amber-200">
          Checkout is not available in this build. Paid plans cannot be purchased yet.
        </div>
        {errorMessage && <p role="alert" className="text-center text-red-300">{errorMessage}</p>}

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {plans.map((plan) => (
            <div
              key={plan.id}
              className={`relative p-8 rounded-3xl border-2 transition-all duration-300 ${plan.borderColor} ${plan.color} ${selectedPlan === plan.id ? 'scale-105 ring-4 ring-indigo-500/30' : 'hover:border-indigo-500/50'}`}
              onClick={() => setSelectedPlan(plan.id)}
            >
              {plan.popular && (
                <div className="absolute -top-4 left-1/2 -translate-x-1/2 bg-indigo-500 text-white text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wider">
                  {t('Most Popular')}
                </div>
              )}
              <div className="text-center mb-8">
                <h3 className="text-2xl font-bold mb-2">{plan.name}</h3>
                <div className="flex items-baseline justify-center gap-1">
                  <span className="text-4xl font-extrabold">${plan.price}</span>
                  <span className="text-slate-400 text-sm">/month</span>
                </div>
                <p className="text-slate-400 mt-4 text-sm leading-relaxed">{plan.description}</p>
              </div>

              <ul className="space-y-4 mb-8">
                {plan.features.map((feat, i) => (
                  <li key={i} className="flex items-start gap-3 text-sm text-slate-300">
                    <span className="text-indigo-400">✓</span> {feat}
                  </li>
                ))}
              </ul>

              <button
                onClick={(e) => {
                  e.stopPropagation();
                  handleUpgrade();
                }}
                disabled={loading || plan.id === 'free' || plan.id !== 'free'}
                className={`w-full py-3 rounded-xl font-bold transition-all ${
                  plan.id === 'free'
                  ? 'bg-slate-700 text-slate-500 cursor-not-allowed'
                  : 'bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-500/20'
                }`}
              >
                {loading ? 'Processing...' : plan.id === 'free' ? plan.buttonText : 'Coming Soon'}
              </button>
            </div>
          ))}
        </div>

        <div className="text-center p-8 bg-slate-800/50 rounded-3xl border border-slate-700">
          <h4 className="text-indigo-300 font-semibold mb-2">{t('Enterprise or Group Plans?')}</h4>
          <p className="text-slate-400 text-sm">{t('Contact our cosmic team for custom solutions and API access.')}</p>
        </div>
      </div>
    </div>
  );
}
