# AstroVerse feature coverage and next work

This list covers the requested astrology features. AstroSage Cloud-style saving, Learn Astrology, Magazine, and AstroSage TV are intentionally excluded.

## Current status

### Tier 1: core

| Feature | Status | Current implementation |
|---|---|---|
| Free Kundli / birth chart | Implemented | Lahiri sidereal natal chart and 16 divisional charts; the form is in onboarding. |
| Kundli matching | Implemented (traditional screening) | Two-person saved-chart comparison with eight itemized Ashtakoota scores, bride/groom orientation, Moon Nakshatra details, Mangal screening, unknown-time handling, and method/limitations. |
| Daily, tomorrow, weekly, and monthly horoscope | Partial | Personalized chart/transit readings exist; daily and tomorrow are now separate. General sign-based Rashifal and deeper editorial report controls remain. |
| Today's Panchang | Partial | Sunrise snapshot has vara, tithi, nakshatra, yoga, karana, sunrise/sunset, and daily timing windows. Transition end-times, lunar month, and festival calendar remain. |

### Tier 2: utilities and reports

| Feature | Status | Current implementation |
|---|---|---|
| Rahu Kaal Today | Implemented | Calculated from local sunrise/sunset and weekday. |
| Choghadiya | Implemented | Eight daylight and eight nighttime intervals using local solar durations. |
| Yearly horoscope | Implemented | 12 chart-based month cards and an annual overview; current sample totals about 756 words. |
| Sade Sati report | Partial | Saturn's position relative to the natal Moon identifies the traditional three-sign window and phase; interpretive report remains. |
| Mangal Dosha report | Partial | Mars houses from Lagna, Moon, and Venus are screened; cancellation rules and full interpretation remain. |
| Kaalsarp Dosha report | Partial | A clearly labelled strict half-chart rule is checked; school-specific variants and interpretation remain. |
| Vimshottari Dasha / Dasha Phal | Partial | Mahadasha and antardasha dates are calculated and shown; personalized period interpretation remains. |
| Varshphal | Not implemented | No annual solar-return chart/report yet. |
| Gochar / transit report | Partial | Current Lahiri transit placements and natal aspects are available; a full period-based report remains. |
| Lal Kitab report | Partial | Lal Kitab house placements are shown; interpretive report remains. |
| Life report | Not implemented | No consolidated printable life report yet. |
| Festival and muhurat pages | Partial | Abhijit Muhurta and daily windows are available; festival dates and dedicated pages remain. |

### Tier 3: occasional calculators

| Feature | Status | Current implementation |
|---|---|---|
| Moon sign calculator | Implemented | Quick Calculators shows the Moon sign from the saved profile's sidereal chart. |
| Sun sign calculator | Implemented | Quick Calculators shows the Sun sign from the saved profile's sidereal chart. |
| Ascendant calculator | Implemented (time-dependent) | Quick Calculators shows the saved Lagna when birth time permits; otherwise it states that time is required. |
| Nakshatra calculator | Implemented | Quick Calculators shows the birth Nakshatra and pada from the saved chart. |
| Numerology calculator | Partial | Pythagorean name number and date-of-birth life path number are available; other numerology schools and compound-number interpretations are not. |
| Love and friendship calculator | Partial | Full birth-data Ashtakoota comparison can be used for relationship reflection; no separate friendship-specific rules or score are provided. |
| Compatibility by name or Moon sign | Partial | A Moon-sign-only comparison shows a basic Bhakoot distance indicator and Moon-sign lord relationship; name-only matching and full eight-koota detail still require birth Nakshatras. |
| Baby name suggestions | Not implemented | No Nakshatra/pada syllable based suggestion catalogue yet. |

## Recently added

- The timing API returns Panchang limbs at local sunrise and 16 location-specific Choghadiya intervals.
- The dashboard timing card displays the five Panchang values and an expandable day/night interval list.
- Astrology Tools includes transparent Mangal Dosha, Kaal Sarpa, and Sade Sati screening rules with method notes.
- Horoscope supports a separate Tomorrow reading; yearly reports include all 12 month sections and chart placements.
- Compatibility provides an authenticated two-person Ashtakoota calculation with eight transparent koota rows and an explicitly non-deterministic interpretation notice.
- Quick Calculators exposes saved-chart Sun, Moon, Ascendant, and Nakshatra/pada results, plus Pythagorean name and life-path numbers.
- Compatibility also offers a clearly limited Moon-sign-only comparison for users who lack complete birth data.

## Verification notes

- Compatibility engine check: eight kootas sum to the expected 36-point maximum; same-sign/same-star sample returned a bounded score and all component rows.
- Backend package import could not be checked in this workspace because the backend virtual environment is absent and system Python does not have FastAPI installed. Use the project's documented environment to install `backend/requirements.txt` before running the server.
- Backend calculation check (reported from prior work): Panchang returned all five values and Choghadiya returned 8 day plus 8 night intervals for a Delhi sample date.
- Backend calculation check: advanced chart response included all three dosha screening results for a sample birth profile.
- Horoscope check: daily, tomorrow, weekly, monthly, and yearly periods generated; yearly output was 756 words with 12 months for the sample chart.
- Frontend TypeScript check: `npx tsc --noEmit` passed after the UI/API changes.
- These readings expose the calculation convention and are traditional astrology interpretations, not guaranteed predictions. Panchang limbs are currently sunrise snapshots; this is not a full almanac with exact transition times or festivals.
