# User Flows & Information Architecture: AstroVerse

## 1. Primary User Journey: The "First Chart" Experience
This is the most critical flow. If this is too complex, users will leave.

**Flow:**
`Landing Page` $\rightarrow$ `Age Gate (18+)` $\rightarrow$ `Auth (Signup/Login)` $\rightarrow$ `Birth Detail Collection` $\rightarrow$ `Chart Calculation` $\rightarrow$ `First Chart View` $\rightarrow$ `Dashboard`

### Detailed Breakdown: Birth Detail Collection
1. **Name:** Input name/nickname.
2. **Date:** Calendar picker for DOB.
3. **Time:** Exact time picker (with "Time Unknown" toggle).
4. **Location:** Search bar with Autocomplete (via Google Places or Mapbox API) $\rightarrow$ Captures City, State, Country, Lat/Long, and Timezone.
5. **Preference:** Select Astrology System (Vedic / Western / Both).

---

## 2. Core Application Map (IA)

### A. Dashboard (The Hub)
- **Current Transit Widget:** What's happening in the sky right now.
- **Daily Horoscope:** Personalized based on Ascendant/Moon.
- **Quick Links:** "Chat with Astro AI," "View My Chart," "Book Consultant."

### B. The Chart Studio
- **View Selector:** Toggle between Natal, Transit, Solar Return, etc.
- **Style Selector:** Circular (Western) vs. Square (North/South Indian).
- **Calculation Toggles:** Ayanamsa, House Systems.
- **Export Button:** Generate PDF/Image.

### C. Astro AI (Chat Interface)
- **Chat Window:** Streaming text responses.
- **Context Bar:** Shows the chart currently being analyzed.
- **Tone Toggle:** (Spiritual / Practical / Detailed).

### D. Marketplace
- **Explorer:** Search astrologers by specialty/rating.
- **Profile Page:** Bio, Pricing, Reviews, Calendar.
- **Booking Flow:** Select Slot $\rightarrow$ Payment $\rightarrow$ Confirmation.

---

## 3. Monetization & Paywall Flow
**Flow:**
`Access Feature (e.g., "Detailed PDF Report")` $\rightarrow$ `Paywall Trigger` $\rightarrow$ `Plan Comparison (Free vs Plus vs Pro)` $\rightarrow$ `Payment Gateway (Stripe/Razorpay)` $\rightarrow$ `Success` $\rightarrow$ `Unlock Feature`
