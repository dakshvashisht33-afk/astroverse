# Astrology feature guide

The dashboard's **Classical chart systems** panel contains the additional tools. The existing **Vedic Birth Charts** panel holds the 16 Shodashavarga charts.

## Included tools

- Lagna and Chandra whole-sign charts, North or South Indian drawing style.
- Sripati-style Bhava Chalit house table and house-placement chart; graha aspects to Bhava Madhya.
- Raw Bhinnashtakavarga and Sarvashtakavarga tables, plus the contributor-level Prastara table.
- KP Placidus cusps, Krishnamurti ayanamsa, star/sub-lords, and sign-based aspects on cusps.
- Natural, temporary, and combined planetary friendship matrix.
- Vimshottari Mahadasha with Antardasha ranges, Yogini Dasha, and a common Jaimini Chara Dasha convention.
- Western tropical planet positions and Placidus cusps.
- Current Lahiri sidereal transits and sign-based Parashari aspects to natal grahas.
- Printable 9×9 Nakshatra frame and a Lagna-based Lal Kitab reference chart.
- Selected bala components with a Bhava occupancy table.

## Calculation notes

- Swiss Ephemeris supplies astronomical positions and house calculations. Vedic charts use Lahiri sidereal positions; the KP panel uses Krishnamurti ayanamsa; the Western panel uses the tropical zodiac.
- The raw Ashtakavarga table follows one documented seven-graha/eight-contributor variant. Its expected checksum is 337. Other textual witnesses and reduction schemes can produce different tables.
- Vimshottari uses the Moon's birth Nakshatra and a 365.2425-day year. Yogini and Chara Dasha conventions vary; the selected rule is displayed with each result.
- Unknown birth time suppresses Ascendant-dependent features. Moon-based placements and dashas use the saved time as an estimate, so their boundary-sensitive results may change when an accurate time is supplied.
- The Shadbala panel does **not** claim a complete six-fold Shadbala or Bhavabala total. It shows only the implemented Uchcha, Dig, and Naisargika components and house occupancy; it withholds a total until the remaining classical calculations are complete and independently reconciled.
- The Sarvatobhadra panel is a printable Nakshatra-only frame. It does not calculate regional syllable/weekday arrangements or Vedha.
- The Lal Kitab panel shows the Lagna-based house placement reference. It does not produce interpretive predictions or remedies.
- Astrological interpretations are traditional symbolic readings and are not empirically verified predictions.

## API

`GET /chart/advanced/{birth_profile_id}` returns the supplementary chart payload for the authenticated user's birth profile.

