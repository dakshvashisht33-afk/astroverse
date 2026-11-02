# Product Requirements Document (PRD): AstroVerse

## 1. Executive Summary
**Project Name:** AstroVerse
**Vision:** A production-grade, multi-tenant astrology platform providing hyper-accurate astrological calculations, AI-driven personalized insights, and a professional marketplace for astrologers.
**Core Value Proposition:** Bridging the gap between traditional astrological wisdom (Vedic & Western) and modern AI scalability, delivered through a premium, trust-oriented user experience.

---

## 2. Target Personas

### 2.1 The Casual Explorer
- **Goal:** Quick daily insights, "fun" compatibility checks, and general zodiac knowledge.
- **Key Needs:** Low friction onboarding, visually appealing UI, easy-to-understand language.

### 2.2 The Serious Practitioner
- **Goal:** In-depth analysis of natal charts, transits, and divisional charts.
- **Key Needs:** Accuracy in degrees/minutes, multiple house systems, Ayanamsa toggles, detailed reports.

### 2.3 The Vedic Specialist
- **Goal:** Traditional Indian astrology tools (Kundli, Dashas, Panchang).
- **Key Needs:** North/South Indian chart styles, Vimshottari Dasha, Ashtakoota matching.

### 2.4 The Professional Astrologer
- **Goal:** Manage a client base, provide consultations, and deliver professional reports.
- **Key Needs:** Booking calendar, client notes, payment dashboard, KYC verification.

### 2.5 The Admin/Operator
- **Goal:** Maintain platform health, safety, and financial integrity.
- **Key Needs:** Content moderation, fraud detection, user management, AI safety logs.

---

## 3. Functional Requirements

### 3.1 Authentication & User Profiles
- **Multi-Channel Auth:** Email/Password, Google OAuth, Apple Sign-In, Phone OTP.
- **Profile Management:** Support for multiple "Birth Profiles" (User, Spouse, Children, Clients).
- **Onboarding Flow:** Step-by-step collection of birth date, exact time, and precise location (integrated with a Geocoding API for Lat/Long/Timezone).
- **Compliance:** GDPR/CCPA data export/deletion and a strict 18+ age gate.

### 3.2 The Astrology Engine (The Core)
- **Calculation Accuracy:** Integration with Swiss Ephemeris (or equivalent) for planetary positions.
- **System Support:** 
    - **Western:** Tropical zodiac, Placidus/Whole Sign houses.
    - **Vedic:** Sidereal zodiac, Lahiri/Raman Ayanamsa, Divisional charts (D1, D9, D10).
- **Chart Generation:** 
    - Natal, Transit, Solar Return, Synastry, and Composite charts.
    - Dynamic rendering of circular (Western) and square (Indian) charts.
- **Export:** High-resolution image and PDF exports for premium reports.

### 3.3 AI Astrology Assistant ("Astro AI")
- **Architecture:** RAG (Retrieval-Augmented Generation).
- **Workflow:** 
    1. Tool computes exact astrological facts $\rightarrow$ 2. Facts passed as context to LLM $\rightarrow$ 3. LLM interprets and converses.
- **Capabilities:** Personalized readings based on the user's current dasha/transit; conversational memory.
- **Personalization:** User-selectable tone (e.g., "Spiritual," "Practical").

### 3.4 Horoscopes & Content
- **Tiers:** Daily, Weekly, Monthly, Yearly.
- **Types:** Sun-sign, Moon-sign, and Ascendant-based.
- **Delivery:** Scheduled publishing via Admin panel; aggressive caching for performance.

### 3.5 Marketplace & Monetization
- **Consultations:** Real-time booking, chat, and video calls for verified astrologers.
- **Monetization Model:** 
    - **Freemium:** Basic charts and daily horoscopes.
    - **Subscriptions:** Unlimited AI questions and advanced reports.
    - **Pay-per-use:** One-time premium reports or consultation credits.
- **Payments:** Stripe (Global) and Razorpay (India).

---

## 4. Non-Functional Requirements

### 4.1 Security & Privacy
- **Data Protection:** HTTPS/HSTS, Argon2id password hashing, and encryption of sensitive birth data at rest.
- **Access Control:** Strict Role-Based Access Control (RBAC) for Users, Astrologers, and Admins.
- **API Security:** Rate limiting, Zod validation, and CSRF protection.

### 4.2 Scalability & Performance
- **Architecture:** Modular Monolith (Next.js + NestJS) to allow future microservice extraction.
- **Performance:** LCP < 2.5s; Redis caching for expensive ephemeris calculations.
- **Availability:** CDN for assets; database read replicas for high-traffic periods.

---

## 5. Legal, Safety & Guardrails

### 5.1 Positioning & Disclaimers
- **Mandatory Label:** "Astrology content is for entertainment and self-reflection purposes only."
- **Prohibited Advice:** AI and human consultants are strictly forbidden from providing medical, legal, or financial guarantees.

### 5.2 AI Safety Rules
- **Hard Blocks:** AI must refuse requests for medical diagnoses, suicide/self-harm advice, or exact dates of death.
- **Crisis Response:** Detection of crisis-related keywords must trigger an immediate stop to astrology and a display of professional help resources.
- **Certainty Guard:** AI must use interpretive language (e.g., "indicates a tendency toward") rather than deterministic claims.

---

## 6. Success Metrics (KPIs)
- **User Growth:** Monthly Active Users (MAU) and Conversion Rate (Free $\rightarrow$ Paid).
- **Technical Health:** API Latency < 200ms; 99.9% Uptime.
- **Retention:** Day-30 retention rate for daily horoscope users.
- **Safety:** Zero instances of medical/legal advice being delivered via AI.
