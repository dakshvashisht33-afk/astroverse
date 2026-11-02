"""Supplementary chart calculations with explicit method labels and limitations."""
from __future__ import annotations

import math
from datetime import date, datetime, time, timedelta
from typing import Any

import swisseph as swe
from zoneinfo import ZoneInfo

from .astrology_engine import engine as astrology_engine
from .planetary_dignity import NATURAL_ENEMIES, NATURAL_FRIENDS, SIGN_LORD
from .transit_engine import transit_engine
from .varga_engine import SIGNS, VARGAS, varga_engine

GRAHAS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
VIM_ORDER = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
VIM_YEARS = dict(zip(VIM_ORDER, [7, 20, 6, 10, 7, 18, 16, 19, 17]))
NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu", "Pushya", "Ashlesha",
    "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati",
]
NAK_LORDS = (VIM_ORDER * 3)

# BPHS/Brihat Jataka style raw Ashtakavarga bindu positions, one-based from
# each of eight contributors: Sun..Saturn and Lagna. Rahu/Ketu are excluded.
BINDU_RULES = {
    "Sun": [[1,2,4,7,8,9,10,11],[3,6,10,11],[1,2,4,7,8,9,10,11],[3,5,6,9,10,11,12],[5,6,9,11],[6,7,12],[1,2,4,7,8,9,10,11],[3,4,6,10,11,12]],
    "Moon": [[3,6,7,8,10,11],[1,3,6,7,10,11],[2,3,5,6,9,10,11],[1,3,4,5,7,8,10,11],[1,4,7,8,10,11,12],[3,4,5,7,9,10,11],[3,5,6,11],[3,6,10,11]],
    "Mars": [[3,5,6,10,11],[3,6,11],[1,2,4,7,8,10,11],[3,5,6,11],[6,10,11,12],[6,8,11,12],[1,4,7,8,9,10,11],[1,3,6,10,11]],
    "Mercury": [[5,6,9,11,12],[2,4,6,8,10,11],[1,2,4,7,8,9,10,11],[1,3,5,6,9,10,11,12],[6,8,11,12],[1,2,3,4,5,8,9,11],[1,2,4,7,8,9,10,11],[1,2,4,6,8,10,11]],
    "Jupiter": [[1,2,3,4,7,8,9,10,11],[2,5,7,9,11],[1,2,4,7,8,10,11],[1,2,4,5,6,9,10,11],[1,2,3,4,7,8,10,11],[2,5,6,9,10,11],[3,5,6,12],[1,2,4,5,6,7,9,10,11]],
    "Venus": [[8,11,12],[1,2,3,4,5,8,9,11,12],[3,5,6,9,11,12],[3,5,6,9,11],[5,8,9,10,11],[1,2,3,4,5,8,9,10,11],[3,4,5,8,9,10,11],[1,2,3,4,5,8,9,11]],
    "Saturn": [[1,2,4,7,8,10,11],[3,6,11],[3,5,6,10,11,12],[6,8,9,10,11,12],[5,6,11,12],[6,11,12],[3,5,6,11],[1,3,4,6,10,11]],
}
BINDU_TOTALS = {"Sun":48,"Moon":49,"Mars":39,"Mercury":54,"Jupiter":56,"Venus":52,"Saturn":39}
NAISARGIKA = {"Sun":60.0,"Moon":51.43,"Mars":17.14,"Mercury":25.71,"Jupiter":34.29,"Venus":42.86,"Saturn":8.57}


def _lon_record(longitude: float, speed: float | None = None) -> dict[str, Any]:
    value = longitude % 360
    return {"longitude": value, "sign_index": int(value // 30), "sign": SIGNS[int(value // 30)], "degree": value % 30, "speed": speed}


def _angular_distance(a: float, b: float) -> float:
    return abs((a - b + 180) % 360 - 180)


def _ordinal(value: int) -> str:
    return {1: "1st", 2: "2nd", 3: "3rd"}.get(value, f"{value}th")


def _nakshatra(longitude: float) -> dict[str, Any]:
    span = 360 / 27
    index = min(26, int((longitude % 360) / span))
    within = ((longitude % 360) - index * span) / span
    return {"index": index, "name": NAKSHATRAS[index], "lord": NAK_LORDS[index], "fraction_elapsed": within, "pada": min(4, int(within * 4) + 1)}


def _kp_sub(longitude: float) -> dict[str, str]:
    star = _nakshatra(longitude)
    start = VIM_ORDER.index(star["lord"])
    pos = star["fraction_elapsed"] * 120
    for step in range(9):
        lord = VIM_ORDER[(start + step) % 9]
        years = VIM_YEARS[lord]
        if pos < years or step == 8:
            return {"nakshatra": star["name"], "star_lord": star["lord"], "sub_lord": lord}
        pos -= years
    return {"nakshatra": star["name"], "star_lord": star["lord"], "sub_lord": VIM_ORDER[start]}


class AdvancedAstrology:
    def calculate(self, dob: date, tob: time, timezone_name: str, latitude: float, longitude: float, time_unknown: bool = False) -> dict[str, Any]:
        local_tz = ZoneInfo(timezone_name)
        birth_local = datetime.combine(dob, tob).replace(tzinfo=local_tz)
        birth_utc = birth_local.astimezone(ZoneInfo("UTC"))
        jd = swe.julday(birth_utc.year, birth_utc.month, birth_utc.day, birth_utc.hour + birth_utc.minute / 60 + birth_utc.second / 3600)
        natal = astrology_engine.calculate_sidereal_planetary_positions(birth_local.replace(tzinfo=None), timezone_name)
        lahiri_houses = None
        kp_houses = None
        try:
            if time_unknown:
                raise ValueError("Unknown birth time: angle-based charts are omitted")
            swe.set_sid_mode(swe.SIDM_LAHIRI)
            lahiri_houses = swe.houses_ex(jd, latitude, longitude, b"P", swe.FLG_SIDEREAL)
            swe.set_sid_mode(swe.SIDM_KRISHNAMURTI)
            kp_houses = swe.houses_ex(jd, latitude, longitude, b"P", swe.FLG_SIDEREAL)
            kp_natal = self._sidereal_planets(jd, swe.SIDM_KRISHNAMURTI)
        except Exception:
            lahiri_houses = kp_houses = None
            kp_natal = None
        finally:
            swe.set_sid_mode(swe.SIDM_LAHIRI)

        asc = float(lahiri_houses[1][0]) % 360 if lahiri_houses else None
        mc = float(lahiri_houses[1][1]) % 360 if lahiri_houses else None
        moon_lon = natal["Moon"]["longitude"]
        lagna_chart = self._reference_chart(natal, asc, "Lagna")
        chandra_chart = self._reference_chart(natal, moon_lon, "Chandra")
        chalit = self._chalit(natal, asc, mc) if asc is not None and mc is not None else None
        ashtaka = self._ashtakavarga(natal, int(asc // 30)) if asc is not None and not time_unknown else None
        friendship = self._friendship(natal)
        dasha = self._vimshottari(moon_lon, birth_local, local_tz)
        yogas = self._yoga_indicators(natal, asc)
        yogini = self._yogini(moon_lon, birth_local, local_tz)
        char_dasha = self._char_dasha(natal, asc, birth_local, local_tz) if asc is not None and not time_unknown else None
        kp = self._kp_cusps(kp_houses) if kp_houses else None
        if kp and kp_natal:
            kp["planets"] = kp_natal
            kp["aspects_on_cusps"] = self._aspects_on_points(kp_natal, [(r["house"], r["longitude"]) for r in kp["cusps"]])
        bhava_aspects = self._aspects_on_points(natal, [(h["house"], h["madhya"]) for h in chalit["houses"]]) if chalit else None
        western = self._western_chart(jd, latitude, longitude, include_houses=not time_unknown)
        transits = transit_engine.get_sidereal_sky(datetime.now(ZoneInfo("UTC")))
        transit_aspects = self._transit_aspects(transits, natal)
        doshas = self._dosha_indicators(natal, asc, transits)
        bala = self._bala_components(natal, asc, mc, chalit)
        planet_insights = self._planet_insights(natal, asc, dasha, bala)
        sbc = self._sarvatobhadra(natal["Moon"]["longitude"])
        lal_kitab = self._lal_kitab(natal, asc)

        return {
            "method": {"vedic": "Swiss Ephemeris, Lahiri sidereal positions; whole-sign D1 and standard Parashari/Ja for each named system.", "western": "Swiss Ephemeris tropical positions with Placidus cusps.", "kp": "Krishnamurti ayanamsa, Placidus cusps, Vimshottari-proportioned star subdivisions.", "unknown_time": "Birth time is marked unknown; ascendant-dependent calculations are withheld. Moon-based periods use the saved time as an estimate." if time_unknown else None},
            "lagna_chart": lagna_chart, "chandra_chart": chandra_chart, "chalit": chalit,
            "bhava_aspects": bhava_aspects, "ashtakavarga": ashtaka, "friendship": friendship,
            "vimshottari": dasha, "yogini": yogini, "char_dasha": char_dasha,
            "kp": kp, "western": western, "transits": {"positions": transits, "aspects": transit_aspects},
            "doshas": doshas,
            "yogas": yogas,
            "planet_insights": planet_insights,
            "bala": bala, "sarvatobhadra": sbc, "lal_kitab": lal_kitab,
            "time_unknown": time_unknown,
        }

    def _yoga_indicators(self, natal: dict[str, Any], asc: float | None) -> dict[str, Any]:
        """Screen common D1 yoga rules; report evidence and avoid treating a match as a promise."""
        if asc is None:
            return {"items": [], "available": False, "method": "A reliable birth time is required for Lagna-based yoga screening."}
        lagna = int(asc // 30)
        house_lords = {house: SIGN_LORD[(lagna + house - 1) % 12] for house in range(1, 13)}
        sign_by_planet = {name: int(position["sign_index"]) for name, position in natal.items()}

        def aspects_sign(planet: str, from_sign: int, target_sign: int) -> bool:
            distance = (target_sign - from_sign) % 12 + 1
            special = {"Mars": {4, 8}, "Jupiter": {5, 9}, "Saturn": {3, 10}}
            return distance == 7 or distance in special.get(planet, set())

        def associated(first: str, second: str) -> tuple[bool, str | None]:
            a, b = sign_by_planet[first], sign_by_planet[second]
            if a == b:
                return True, "conjunction by sign"
            if aspects_sign(first, a, b) or aspects_sign(second, b, a):
                return True, "Parashari planetary aspect"
            if SIGN_LORD[a] == second and SIGN_LORD[b] == first:
                return True, "mutual sign exchange"
            return False, None

        items: list[dict[str, Any]] = []
        kendra = {1, 4, 7, 10}
        trikona = {1, 5, 9}

        def add(name: str, category: str, planets: list[str], houses: list[int], basis: str,
                interpretation: str, modifiers: list[str] | None = None, source: str = "") -> None:
            items.append({"name": name, "category": category, "planets": planets,
                          "houses": houses, "basis": basis, "interpretation": interpretation,
                          "modifiers_to_review": modifiers or [], "classical_reference": source,
                          "status": "rule matched; assess strength and exceptions"})

        for k_house in sorted(kendra):
            for t_house in sorted(trikona):
                if k_house == t_house:
                    continue
                first, second = house_lords[k_house], house_lords[t_house]
                if first == second:
                    continue
                present, rule = associated(first, second)
                if present:
                    add("Kendra-Trikona Raja Yoga", "Raja", [first, second], sorted({k_house, t_house}),
                        f"Lords of houses {k_house} and {t_house} form {rule}.",
                        "Traditionally links action or public responsibility with purpose and opportunity. The result depends on functional lordship, dignity, affliction, and operating periods.",
                        ["Check whether the lords are combust, debilitated, heavily afflicted, or otherwise weak.",
                         "A sambandha can be defined differently across Parashari schools."], "BPHS, Raja Yoga chapter")

        dharma_lord, karma_lord = house_lords[9], house_lords[10]
        if dharma_lord != karma_lord:
            present, rule = associated(dharma_lord, karma_lord)
            if present:
                add("Dharma-Karmadhipati Raja Yoga", "Raja", [dharma_lord, karma_lord], [9, 10],
                    f"Ninth and tenth lords form {rule}.",
                    "Traditionally links principles, teachers, or long-range learning with work and responsibility; it does not guarantee status or a particular career outcome.",
                    ["Assess both lords' dignity, house placement, aspects, and dasha activation."], "BPHS, Raja Yoga chapter")

        mahapurusha = {
            "Mars": ("Ruchaka Yoga", {0, 7, 9}), "Mercury": ("Bhadra Yoga", {2, 5}),
            "Jupiter": ("Hamsa Yoga", {8, 11, 3}), "Venus": ("Malavya Yoga", {1, 6, 11}),
            "Saturn": ("Shasha Yoga", {9, 10, 6}),
        }
        for planet, (name, eligible_signs) in mahapurusha.items():
            sign = sign_by_planet[planet]
            house = (sign - lagna) % 12 + 1
            if sign in eligible_signs and house in kendra:
                add(name, "Mahapurusha", [planet], [house],
                    f"{planet} is in its own or exaltation sign and a kendra (house {house}).",
                    "A classical prominence/strength combination. Its expression depends on exact dignity, functional role, affliction, divisional support, and operating periods.",
                    ["Verify the planet is not materially weakened by combustion, debility cancellation details, or severe affliction."],
                    "BPHS, Mahapurusha Yoga chapter")

        # Common Viparita Raja Yoga screening: a dusthana lord occupies a dusthana.
        # School definitions and exceptions vary, so each result carries its exact trigger.
        for house, name in ((6, "Harsha Yoga"), (8, "Sarala Yoga"), (12, "Vimala Yoga")):
            planet = house_lords[house]
            occupied = (sign_by_planet[planet] - lagna) % 12 + 1
            if occupied in {6, 8, 12}:
                add(name, "Viparita Raja", [planet], [house, occupied],
                    f"Lord of the {house}th house ({planet}) occupies the {occupied}th house.",
                    "Traditional readings associate this dusthana-lord relationship with handling setbacks, obligations, or hidden pressures in an unusual way. It is not a guarantee of success or immunity from difficulty.",
                    ["Review the other dusthana lords, conjunctions, aspects, dignity, and dasha before judging results."],
                    "BPHS, Raja Yoga chapter; later Parashari practice")

        # Dhana yoga screening uses 2nd/11th wealth houses and 5th/9th trikonas.
        wealth_houses, fortune_houses = (2, 11), (5, 9)
        seen_dhana: set[tuple[str, str, int, int]] = set()
        for wealth_house in wealth_houses:
            for fortune_house in fortune_houses:
                first, second = house_lords[wealth_house], house_lords[fortune_house]
                if first == second:
                    continue
                present, rule = associated(first, second)
                key = (first, second, wealth_house, fortune_house)
                if present and key not in seen_dhana:
                    seen_dhana.add(key)
                    add("Dhana Yoga", "Wealth", [first, second], [wealth_house, fortune_house],
                        f"Lords of houses {wealth_house} and {fortune_house} form {rule}.",
                        "A traditional resource/opportunity linkage. It describes a chart factor, not a promise of income; effort, context, and the full chart matter.",
                        ["Assess the 2nd, 11th, 5th, and 9th lords together, plus affliction and dasha."],
                        "BPHS, Yogakaraka and Wealth Yoga chapters")

        jupiter_from_moon = (sign_by_planet["Jupiter"] - sign_by_planet["Moon"]) % 12 + 1
        if jupiter_from_moon in kendra:
            add("Gaja Kesari Yoga", "Lunar", ["Moon", "Jupiter"], [jupiter_from_moon],
                f"Jupiter is {jupiter_from_moon} sign(s) from the Moon, a kendra relationship.",
                "Traditionally associated with learning, judgment, and support. A sign-only match can be substantially modified by strength, affliction, and chart context.",
                ["This screen does not apply every classical qualification or cancellation."], "BPHS, Chandra/Jupiter Yoga chapter")
        if sign_by_planet["Sun"] == sign_by_planet["Mercury"]:
            add("Budha-Aditya Yoga", "Conjunction", ["Sun", "Mercury"], [],
                "Sun and Mercury occupy the same sign.",
                "Traditionally links intellect, communication, and visibility; conjunction quality and combustion materially modify interpretation.",
                ["Review exact longitudinal separation and Mercury's combustion status."], "BPHS, Solar Yoga chapter")
        if sign_by_planet["Moon"] == sign_by_planet["Mars"]:
            add("Chandra-Mangala Yoga", "Conjunction", ["Moon", "Mars"], [],
                "Moon and Mars occupy the same sign.",
                "Traditionally connects initiative with emotional or material drive; the chart context changes how this is expressed.",
                ["Review exact separation, lunar condition, house lordships, and affliction."], "Common Parashari practice")

        # Adhi Yoga: natural benefics in the 6th, 7th, and/or 8th from the Moon.
        benefic_houses = {name: (sign_by_planet[name] - sign_by_planet["Moon"]) % 12 + 1
                          for name in ("Jupiter", "Venus", "Mercury")}
        adhi = {name: house for name, house in benefic_houses.items() if house in {6, 7, 8}}
        if adhi:
            add("Adhi Yoga", "Lunar", list(adhi), sorted(adhi.values()),
                "Natural benefic planet(s) " + ", ".join(f"{name} in {house}th from Moon" for name, house in adhi.items()) + ".",
                "A traditional Moon-based support combination; benefic condition and affliction determine how supportive it may feel.",
                ["This is a sign-based screen and does not grade full planetary strength."], "BPHS, Lunar Yoga chapter")

        # Amala Yoga: natural benefic in the 10th from Lagna or Moon.
        amala: list[str] = []
        for reference_name, reference_sign in (("Lagna", lagna), ("Moon", sign_by_planet["Moon"])):
            for planet in ("Jupiter", "Venus", "Mercury"):
                if (sign_by_planet[planet] - reference_sign) % 12 + 1 == 10:
                    amala.append(f"{planet} 10th from {reference_name}")
        if amala:
            add("Amala Yoga", "Reputation", sorted({row.split()[0] for row in amala}), [10],
                "; ".join(amala) + ".",
                "Traditionally emphasizes constructive public contribution or reputation; actual outcomes remain dependent on the complete chart and periods.",
                ["Check benefic strength, affliction, and whether the reference is Lagna or Moon."], "BPHS, Lunar/planetary Yoga chapters")

        # Neecha-bhanga is reported only as cancellation indications, not as automatic Raja Yoga.
        exalted_sign = {"Sun": 0, "Moon": 1, "Mars": 9, "Mercury": 5,
                        "Jupiter": 3, "Venus": 11, "Saturn": 6}
        for planet, position in natal.items():
            if position.get("dignity") != "Debilitated":
                continue
            debilitated_sign = sign_by_planet[planet]
            sign_dispositor = SIGN_LORD[debilitated_sign]
            exaltation_sign_lord = SIGN_LORD[exalted_sign[planet]]
            indicators = []
            for reference, reference_sign in (("Lagna", lagna), ("Moon", sign_by_planet["Moon"])):
                disp_house = (sign_by_planet[sign_dispositor] - reference_sign) % 12 + 1
                exalt_lord_house = (sign_by_planet[exaltation_sign_lord] - reference_sign) % 12 + 1
                if disp_house in kendra:
                    indicators.append(f"dispositor {sign_dispositor} is in kendra from {reference}")
                if exalt_lord_house in kendra:
                    indicators.append(f"exaltation-sign lord {exaltation_sign_lord} is in kendra from {reference}")
            own_house = (sign_by_planet[planet] - lagna) % 12 + 1
            if own_house in kendra:
                indicators.append(f"debilitated {planet} itself is in a kendra from Lagna")
            if indicators:
                add("Neecha-bhanga indicator", "Dignity modification", [planet, sign_dispositor, exaltation_sign_lord],
                    [own_house], "Debilitated placement with possible cancellation condition(s): " + "; ".join(dict.fromkeys(indicators)) + ".",
                    "Some traditions treat these conditions as reducing debility. Cancellation does not automatically create Neecha-bhanga Raja Yoga; strength and additional Raja-yoga conditions must be assessed separately.",
                    ["Different classical and lineage rules use different cancellation conditions.", "The chart engine does not claim a definitive Neecha-bhanga Raja Yoga."],
                    "BPHS, dignity and Raja Yoga chapters; rule variants exist")

        # Remove duplicate Raja Yoga pairs while retaining distinct house links.
        unique: dict[tuple[str, tuple[str, ...], tuple[int, ...]], dict[str, Any]] = {}
        for item in items:
            key = (item["name"], tuple(sorted(item["planets"])), tuple(item["houses"]))
            unique[key] = item
        return {"items": list(unique.values()), "available": True,
                "method": "Transparent D1 screening of selected common Parashari combinations (Raja, Dhana, Viparita, Mahapurusha, Lunar, and dignity-modification indicators). Sign-level aspects/associations and classical qualifications vary by source and lineage. This is not an exhaustive yoga catalogue: divisional validation, complete shadbala, all cancellations, combustion/avastha refinements, and school-specific exceptions are not fully modeled. A match is an interpretation lead, not a prediction or promise."}

    def _planet_insights(self, natal: dict[str, Any], asc: float | None, dasha: dict[str, Any], bala: dict[str, Any]) -> list[dict[str, Any]]:
        """Offer qualitative, auditable D1 summaries and dasha activation dates."""
        if asc is None:
            return []
        lagna = int(asc // 30)
        house_meanings = {
            1: "identity, vitality, and self-directed choices", 2: "resources, speech, and family values",
            3: "skills, communication, and sustained effort", 4: "home, foundations, and inner steadiness",
            5: "learning, creativity, and considered risks", 6: "service, routines, and problem-solving",
            7: "partnerships, agreements, and collaboration", 8: "change, research, and shared resources",
            9: "principles, mentors, and long-range learning", 10: "career, contribution, and responsibility",
            11: "networks, gains, and long-term aims", 12: "rest, retreat, and behind-the-scenes work",
        }
        periods = dasha.get("periods", [])
        today = dasha.get("as_of") or datetime.now().date().isoformat()
        special_aspects = {"Mars": {4, 8}, "Jupiter": {5, 9}, "Saturn": {3, 10}}
        bala_by_planet = {row["planet"]: row for row in bala.get("planetary", [])}
        output = []
        for planet, position in natal.items():
            sign_index = int(position["sign_index"])
            house = (sign_index - lagna) % 12 + 1
            dignity = position.get("dignity", "Not classified")
            owned_houses = [h for h in range(1, 13) if SIGN_LORD[(lagna + h - 1) % 12] == planet]
            conjunct = [name for name, other in natal.items() if name != planet and int(other["sign_index"]) == sign_index]
            aspected_by = []
            for other_name, other in natal.items():
                if other_name == planet or other_name not in GRAHAS:
                    continue
                distance = (sign_index - int(other["sign_index"])) % 12 + 1
                if distance == 7 or distance in special_aspects.get(other_name, set()):
                    aspected_by.append(other_name)
            score = {"Exalted": 2, "Own sign": 2, "Friendly sign": 1, "Neutral sign": 0,
                     "Enemy sign": -1, "Debilitated": -2}.get(dignity, 0)
            # House placement is reported as context, not a universal good/bad score.
            score += 1 if house in {1, 5, 9, 10, 11} else (-1 if house in {6, 8, 12} else 0)
            # The influence adjustment is deliberately small; aspects are not a
            # substitute for full shadbala, combustion, avastha, or cancellation analysis.
            score += sum(1 for name in aspected_by if name == "Jupiter")
            score -= sum(1 for name in aspected_by if name in {"Mars", "Saturn"})
            score += sum(1 for name in conjunct if name in {"Jupiter", "Venus"})
            score -= sum(1 for name in conjunct if name in {"Mars", "Saturn"})
            bala_factors = bala_by_planet.get(planet, {})
            uccha = bala_factors.get("uchcha_bala")
            dig = bala_factors.get("dig_bala")
            if uccha is not None:
                score += 1 if uccha >= 45 else (-1 if uccha < 15 else 0)
            if dig is not None:
                score += 1 if dig >= 45 else (-1 if dig < 15 else 0)
            if score >= 2:
                potential = "Strong supportive potential"
            elif score >= 1:
                potential = "Supportive potential"
            elif score <= -2:
                potential = "Needs more conscious effort"
            elif score < 0:
                potential = "Mixed; develops through effort"
            else:
                potential = "Context-dependent potential"
            ownership = (" It also rules house(s) " + ", ".join(map(str, owned_houses)) + ".") if owned_houses else ""
            association = (f" It shares its sign with {', '.join(conjunct)}." if conjunct else "")
            aspect_note = (f" It receives Parashari aspects from {', '.join(aspected_by)}." if aspected_by else "")
            factors = [f"{dignity} sign dignity", f"whole-sign house {house}"]
            if owned_houses:
                factors.append("lord of house(s) " + ", ".join(map(str, owned_houses)))
            if conjunct:
                factors.append("conjunct " + ", ".join(conjunct))
            if aspected_by:
                factors.append("aspected by " + ", ".join(aspected_by))
            if uccha is not None:
                factors.append(f"partial Uchcha Bala {uccha:.1f}/60")
            if dig is not None:
                factors.append(f"partial Dig Bala {dig:.1f}/60")
            timing = []
            for row in periods:
                if row.get("lord") == planet and row.get("end", "") >= today:
                    timing.append({"period": "Mahadasha", "start": row["start"], "end": row["end"],
                                   "status": "current" if row.get("start", "") <= today <= row.get("end", "") else "upcoming"})
                for antar in row.get("antardashas", []):
                    if antar.get("lord") == planet and antar.get("end", "") >= today:
                        timing.append({"period": f"Antardasha · {row.get('lord')} Mahadasha",
                                       "start": antar["start"], "end": antar["end"],
                                       "status": "current" if antar.get("start", "") <= today <= antar.get("end", "") else "upcoming"})
            timing.sort(key=lambda item: (item["start"], item["period"]))
            timing = timing[:5]
            output.append({"planet": planet, "sign": position["sign"], "degree": round(position["degree"], 2),
                           "house": house, "dignity": dignity, "owned_houses": owned_houses,
                           "potential": potential,
                           "potential_factors": factors,
                           "influences": {"conjunct_planets": conjunct, "aspected_by": aspected_by},
                           "insight": f"In house {house}, this planet brings attention to {house_meanings[house]}.{ownership}{association}{aspect_note}",
                           "activation_periods": timing,
                           "potential_method": "Qualitative D1 screen: classical sign dignity, whole-sign house context, functional lordship, same-sign conjunctions, classical Parashari aspects, and available partial Uchcha/Dig Bala. Not full Shadbala or a deterministic outcome."})
        return output

    def _dosha_indicators(self, natal: dict[str, Any], asc: float | None, transits: dict[str, Any]) -> dict[str, Any]:
        """Expose transparent traditional screening rules, not deterministic predictions."""
        mars_sign = natal["Mars"]["sign_index"]
        moon_sign = natal["Moon"]["sign_index"]
        venus_sign = natal["Venus"]["sign_index"]
        mangal_houses = {"Lagna": ((mars_sign - int(asc // 30)) % 12) + 1 if asc is not None else None,
                         "Moon": ((mars_sign - moon_sign) % 12) + 1,
                         "Venus": ((mars_sign - venus_sign) % 12) + 1}
        mangal_trigger_houses = {1, 2, 4, 7, 8, 12}
        mars_flags = {reference: house in mangal_trigger_houses if house is not None else None for reference, house in mangal_houses.items()}

        rahu = natal["Rahu"]["longitude"]
        classical = [natal[name]["longitude"] for name in GRAHAS]
        offsets = [(longitude - rahu) % 360 for longitude in classical]
        kaal_sarpa = all(offset <= 180 for offset in offsets) or all(offset >= 180 for offset in offsets)

        saturn_sign = transits.get("Saturn", {}).get("sign_index")
        relative = (saturn_sign - moon_sign) % 12 if saturn_sign is not None else None
        sade_sati = relative in {11, 0, 1} if relative is not None else False
        phase = {11: "entering (12th from natal Moon)", 0: "middle (over natal Moon)", 1: "exiting (2nd from natal Moon)"}.get(relative)
        return {
            "mangal_dosha": {"present_by_reference": mars_flags, "mars_houses": mangal_houses,
                "trigger_houses": sorted(mangal_trigger_houses), "method": "Screening rule: Mars in houses 1, 2, 4, 7, 8, or 12 from Lagna, Moon, or Venus. Traditions differ; cancellation rules are not applied."},
            "kaal_sarpa": {"present_by_strict_half_chart_rule": kaal_sarpa,
                "method": "Screening rule: all seven classical planets lie in one semicircle from Rahu to Ketu. Schools vary on node conjunctions, exceptions, and interpretation."},
            "sade_sati": {"active": sade_sati, "phase": phase, "natal_moon_sign": SIGNS[moon_sign], "transit_saturn_sign": SIGNS[saturn_sign] if saturn_sign is not None else None,
                "method": "Transit Saturn in the sign before, same as, or after the natal Moon sign. This is a transit status, not an outcome prediction."},
        }

    def _reference_chart(self, natal: dict[str, Any], reference_lon: float | None, label: str) -> dict[str, Any]:
        ref = int(reference_lon // 30) if reference_lon is not None else None
        entries = []
        for name, pos in natal.items():
            entries.append({"planet": name, **pos, "house": ((pos["sign_index"] - ref) % 12 + 1) if ref is not None else None})
        return {"reference": label, "reference_sign": SIGNS[ref] if ref is not None else None, "reference_sign_index": ref, "planets": entries}

    def _chalit(self, natal: dict[str, Any], asc: float, mc: float) -> dict[str, Any]:
        # Sripati-style bhava madhyas: 1/4/7/10 centers at Asc/IC/Desc/MC,
        # with intermediate centers trisected along each zodiacal quadrant.
        mids = [0.0] * 12
        cardinals = {0: asc, 3: (mc + 180) % 360, 6: (asc + 180) % 360, 9: mc}
        keys = [0, 3, 6, 9, 12]
        vals = [asc, cardinals[3], cardinals[6], cardinals[9], (asc + 360) % 360]
        for qi in range(4):
            start, end = vals[qi], vals[qi + 1]
            arc = (end - start) % 360
            for j in range(4): mids[(keys[qi] + j) % 12] = (start + arc * j / 3) % 360
        # Bhava boundaries are the midpoints between adjacent bhava centers.
        boundaries = [((mids[(i - 1) % 12] + ((mids[i] - mids[(i - 1) % 12]) % 360) / 2) % 360) for i in range(12)]
        houses = []
        for i in range(12):
            start, end = boundaries[i], boundaries[(i + 1) % 12]
            planets = []
            for name, pos in natal.items():
                lon = pos["longitude"]
                inside = ((lon - start) % 360) < ((end - start) % 360)
                if inside: planets.append(name)
            houses.append({"house": i + 1, "start_cusp": start, "madhya": mids[i], "end_cusp": end, "planets": planets})
        return {"system": "Sripati bhava madhya from Lahiri ascendant/MC", "houses": houses, "planet_houses": {name: next((h["house"] for h in houses if name in h["planets"]), None) for name in natal}}

    def _ashtakavarga(self, natal: dict[str, Any], lagna_sign: int) -> dict[str, Any]:
        refs = [natal[p]["sign_index"] for p in GRAHAS] + [lagna_sign]
        rows = {}
        contributors = GRAHAS + ["Lagna"]
        for recipient, rules in BINDU_RULES.items():
            by_contributor = []
            totals = [0] * 12
            for contributor, source_sign, good_positions in zip(contributors, refs, rules):
                bits = [1 if ((sign - source_sign) % 12 + 1) in good_positions else 0 for sign in range(12)]
                by_contributor.append({"contributor": contributor, "bindus": bits})
                totals = [a + b for a, b in zip(totals, bits)]
            rows[recipient] = {"bindus": totals, "total": sum(totals), "prastara": by_contributor}
        sav = [sum(rows[p]["bindus"][i] for p in GRAHAS) for i in range(12)]
        return {"signs": SIGNS, "rows": rows, "sarva": sav, "total": sum(sav), "expected_total": 337, "method": "Unreduced seven-graha BAV; eight contributors include Lagna; Rahu/Ketu excluded."}

    def _friendship(self, natal: dict[str, Any]) -> dict[str, Any]:
        matrix = []
        for a in GRAHAS:
            row = []
            for b in GRAHAS:
                if a == b:
                    row.append({"planet": b, "natural": "Self", "temporary": "Self", "compound": "Self"}); continue
                lord = SIGN_LORD[natal[b]["sign_index"]]
                if lord == a: natural = "Own sign"
                elif lord in NATURAL_FRIENDS[a]: natural = "Friend"
                elif lord in NATURAL_ENEMIES[a]: natural = "Enemy"
                else: natural = "Neutral"
                relative = (natal[b]["sign_index"] - natal[a]["sign_index"]) % 12 + 1
                temporary = "Friend" if relative in {2,3,4,10,11,12} else "Enemy"
                compound = {("Friend","Friend"):"Great friend",("Friend","Enemy"):"Neutral",("Neutral","Friend"):"Friend",("Neutral","Enemy"):"Enemy",("Enemy","Friend"):"Neutral",("Enemy","Enemy"):"Great enemy"}.get((natural, temporary), natural)
                row.append({"planet": b, "natural": natural, "temporary": temporary, "compound": compound})
            matrix.append({"planet": a, "relations": row})
        return {"planets": GRAHAS, "matrix": matrix, "method": "Natural relationship plus temporary relationship by mutual sign distance; compound five-fold labels."}

    def _vimshottari(self, moon_lon: float, birth: datetime, tz: ZoneInfo) -> dict[str, Any]:
        star = _nakshatra(moon_lon); lord = star["lord"]; idx = VIM_ORDER.index(lord)
        balance = VIM_YEARS[lord] * (1 - star["fraction_elapsed"])
        cursor = birth
        periods = []
        for n in range(18):
            planet = VIM_ORDER[(idx + n) % 9]
            full_years = VIM_YEARS[planet]
            years = balance if n == 0 else full_years
            end = cursor + timedelta(days=years * 365.2425)
            actual_start = birth - timedelta(days=full_years * star["fraction_elapsed"] * 365.2425) if n == 0 else cursor
            # Keep nested periods for the whole generated horizon so every
            # planet can show upcoming Antardasha windows.
            antar = self._antardashas(planet, full_years, actual_start, tz, lower_bound=birth if n == 0 else None)
            periods.append({"lord": planet, "start": cursor.astimezone(tz).date().isoformat(), "end": end.astimezone(tz).date().isoformat(), "years": round(years, 3), "antardashas": antar})
            cursor = end
            balance = 0
        current = next((p for p in periods if p["start"] <= datetime.now(tz).date().isoformat() <= p["end"]), None)
        return {"birth_nakshatra": star, "periods": periods, "current": current, "as_of": datetime.now(tz).date().isoformat(), "method": "Moon nakshatra balance and 120-year Vimshottari proportions; 365.2425-day dasha year."}

    def _antardashas(self, md_lord: str, md_years: float, start: datetime, tz: ZoneInfo, lower_bound: datetime | None = None) -> list[dict[str, Any]]:
        first = VIM_ORDER.index(md_lord); cursor = start; rows=[]
        for i in range(9):
            lord = VIM_ORDER[(first+i)%9]; years = md_years * VIM_YEARS[lord] / 120
            end = cursor + timedelta(days=years * 365.2425)
            if lower_bound is None or end > lower_bound:
                visible_start=max(cursor,lower_bound) if lower_bound else cursor
                rows.append({"lord": lord, "start": visible_start.astimezone(tz).date().isoformat(), "end": end.astimezone(tz).date().isoformat()})
            cursor = end
        return rows

    def _yogini(self, moon_lon: float, birth: datetime, tz: ZoneInfo) -> dict[str, Any]:
        names = ["Mangala", "Pingala", "Dhanya", "Bhramari", "Bhadrika", "Ulka", "Siddha", "Sankata"]
        lords = ["Moon", "Sun", "Jupiter", "Mars", "Mercury", "Saturn", "Venus", "Rahu"]
        years = [1,2,3,4,5,6,7,8]
        star = _nakshatra(moon_lon); start = (star["index"] + 3) % 8
        balance = years[start] * (1 - star["fraction_elapsed"])
        cursor = birth
        rows=[]
        for i in range(24):
            j=(start+i)%8; duration=balance if i==0 else years[j]
            end=cursor+timedelta(days=duration*365.2425)
            rows.append({"yogini":names[j],"lord":lords[j],"start":cursor.astimezone(tz).date().isoformat(),"end":end.astimezone(tz).date().isoformat(),"years":round(duration,3)})
            cursor=end; balance=0
        today=datetime.now(tz).date().isoformat()
        return {"birth_nakshatra":star,"periods":rows,"current":next((r for r in rows if r['start']<=today<=r['end']),None),"method":"36-year eight-Yogini cycle; starting Yogini indexed from Janma Nakshatra; school conventions vary."}

    def _char_dasha(self, natal: dict[str, Any], asc: float, birth: datetime, tz: ZoneInfo) -> dict[str, Any]:
        start_sign=int(asc//30); odd=(start_sign%2==0); step=1 if odd else -1
        rows=[]; cursor=birth
        for cycle in range(2):
            for i in range(12):
                sign=(start_sign+step*i)%12
                lord=SIGN_LORD[sign]
                if sign==7: lord="Mars"  # Scorpio: Mars co-lord in this common Chara convention.
                if sign==10: lord="Saturn" # Aquarius: Saturn co-lord.
                lord_sign=natal[lord]["sign_index"]
                count=((lord_sign-sign)*step)%12
                years=count or 12
                end=cursor+timedelta(days=years*365.2425)
                rows.append({"sign":SIGNS[sign],"lord":lord,"start":cursor.astimezone(tz).date().isoformat(),"end":end.astimezone(tz).date().isoformat(),"years":years})
                cursor=end
        today=datetime.now(tz).date().isoformat()
        return {"periods":rows,"current":next((r for r in rows if r['start']<=today<=r['end']),None),"method":"Common Jaimini sign-period convention: direction by odd/even starting sign; duration counted to sign lord. Multiple traditions differ."}

    def _kp_cusps(self, houses: Any) -> dict[str, Any] | None:
        if not houses: return None
        cusps=houses[0]; rows=[]
        for i, raw in enumerate(cusps):
            lon=float(raw)%360; kp=_kp_sub(lon)
            rows.append({"house":i+1,**_lon_record(lon),**kp})
        return {"cusps":rows,"ayanamsa":"Krishnamurti","method":"Placidus cusps; KP star/sub boundaries use Vimshottari proportions."}

    def _sidereal_planets(self, jd: float, mode: int) -> dict[str, Any]:
        swe.set_sid_mode(mode)
        flags=swe.FLG_SWIEPH|swe.FLG_SIDEREAL|swe.FLG_SPEED
        bodies={"Sun":swe.SUN,"Moon":swe.MOON,"Mars":swe.MARS,"Mercury":swe.MERCURY,"Jupiter":swe.JUPITER,"Venus":swe.VENUS,"Saturn":swe.SATURN,"Rahu":swe.MEAN_NODE}
        output={}
        for name,body in bodies.items():
            result,_=swe.calc_ut(jd,body,flags); output[name]=_lon_record(result[0],result[3]); output[name]["retrograde"]=result[3]<0
        output["Ketu"]=_lon_record(output["Rahu"]["longitude"]+180,output["Rahu"]["speed"])
        return output

    def _aspects_on_points(self, planets: dict[str, Any], points: list[tuple[int,float]]) -> list[dict[str, Any]]:
        result=[]
        aspect_houses={"Mars":{4,7,8},"Jupiter":{5,7,9},"Saturn":{3,7,10}}
        for house,point in points:
            target_sign=int(point//30)
            for name,pos in planets.items():
                if name not in GRAHAS: continue
                offset=(target_sign-pos["sign_index"])%12+1
                allowed=aspect_houses.get(name,{7})
                if offset in allowed:
                    result.append({"house":house,"target_longitude":round(point,5),"planet":name,"aspect_house":offset,"aspect_label":_ordinal(offset),"separation_degrees":round(_angular_distance(point,pos["longitude"]),3)})
        return result

    def _western_chart(self, jd: float, lat: float, lon: float, include_houses: bool = True) -> dict[str, Any]:
        bodies={"Sun":swe.SUN,"Moon":swe.MOON,"Mercury":swe.MERCURY,"Venus":swe.VENUS,"Mars":swe.MARS,"Jupiter":swe.JUPITER,"Saturn":swe.SATURN,"Uranus":swe.URANUS,"Neptune":swe.NEPTUNE,"Pluto":swe.PLUTO}
        pos={}
        for name, body in bodies.items():
            result,_=swe.calc_ut(jd,body,swe.FLG_SWIEPH|swe.FLG_SPEED); pos[name]=_lon_record(result[0],result[3])
        try:
            if not include_houses: raise ValueError("Birth time unknown")
            cusps, angles=swe.houses_ex(jd,lat,lon,b"P",0)
            houses=[{"house":i+1,"cusp":float(v)%360} for i,v in enumerate(cusps)]
            angles={"ascendant":float(angles[0])%360,"midheaven":float(angles[1])%360}
        except Exception:
            houses=[]; angles=None
        return {"planets":pos,"houses":houses,"angles":angles,"method":"Tropical geocentric zodiac; Placidus houses."}

    def _transit_aspects(self, transits: dict[str, Any], natal: dict[str, Any]) -> list[dict[str, Any]]:
        aspects=[]
        vedic_houses={"Mars":{4,7,8},"Jupiter":{5,7,9},"Saturn":{3,7,10}}
        for tname,tpos in transits.items():
            if tname not in GRAHAS: continue
            for nname,npos in natal.items():
                if nname not in GRAHAS: continue
                aspect_house=(npos["sign_index"]-tpos["sign_index"])%12+1
                if aspect_house in vedic_houses.get(tname,{7}):
                    aspects.append({"transiting":tname,"natal":nname,"aspect":f"{_ordinal(aspect_house)} sign aspect","separation":round(_angular_distance(tpos["longitude"],npos["longitude"]),2)})
        return aspects

    def _bala_components(self, natal: dict[str, Any], asc: float | None, mc: float | None, chalit: dict[str, Any] | None) -> dict[str, Any]:
        rows=[]
        weak_points={"Sun":(mc+180)%360 if mc is not None else None,"Mars":(mc+180)%360 if mc is not None else None,"Moon":mc,"Venus":mc,"Jupiter":(asc+180)%360 if asc is not None else None,"Mercury":(asc+180)%360 if asc is not None else None,"Saturn":asc}
        deep_debilitation={"Sun":190,"Moon":213,"Mars":118,"Mercury":345,"Jupiter":275,"Venus":177,"Saturn":20}
        for name in GRAHAS:
            lon=natal[name]["longitude"]
            uccha=_angular_distance(lon,deep_debilitation[name])/3
            weak=weak_points[name]
            dig=(_angular_distance(lon,weak)/3) if weak is not None else None
            rows.append({"planet":name,"uchcha_bala":round(uccha,2),"dig_bala":round(dig,2) if dig is not None else None,"naisargika_bala":NAISARGIKA[name]})
        bhava=[]
        if chalit:
            for item in chalit["houses"]:
                occupants=item["planets"]
                bhava.append({"house":item["house"],"madhya":round(item["madhya"],4),"occupants":occupants,"occupant_count":len(occupants)})
        return {"planetary":rows,"bhava":bhava,"status":"Only Uchcha, Dig, and Naisargika components are shown. Full Shadbala and Bhavabala totals are intentionally withheld until every classical component is implemented and independently reconciled.","method":"Uchcha: distance from exact deep-debilitation degree divided by 3; Dig: distance from classical weakest direction divided by 3; Naisargika: fixed classical natural strength."}

    def _sarvatobhadra(self, moon_lon: float) -> dict[str, Any]:
        # 9x9 Sarvatobhadra grid: perimeter encodes nakshatras; center is retained
        # as a clear printable board. A full regional akshara/vedha layout varies.
        star=_nakshatra(moon_lon)
        perimeter=["Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra","Punarvasu","Pushya","Ashlesha","Magha","Purva Phalguni","Uttara Phalguni","Hasta","Chitra","Swati","Vishakha","Anuradha","Jyeshtha","Mula","Purva Ashadha","Uttara Ashadha","Abhijit","Shravana","Dhanishta","Shatabhisha","Purva Bhadrapada","Uttara Bhadrapada","Revati"]
        grid=[["" for _ in range(9)] for _ in range(9)]
        coords=[(0,i) for i in range(1,8)]+[(i,8) for i in range(1,8)]+[(8,i) for i in range(7,0,-1)]+[(i,0) for i in range(7,0,-1)]
        for i,(r,c) in enumerate(coords): grid[r][c]=perimeter[i]
        selected=perimeter.index(star["name"])
        r,c=coords[selected]; grid[r][c]="★ "+grid[r][c]
        grid[4][4]="Moon · "+star["name"]
        return {"grid":grid,"birth_nakshatra":star,"method":"Printable nakshatra-only 9×9 Sarvatobhadra frame. Syllables, weekday, rāśi and vedha features are omitted because regional layouts/rules vary."}

    def _lal_kitab(self, natal: dict[str, Any], asc: float | None) -> dict[str, Any]:
        if asc is None:return {"houses":[],"notice":"Birth time is required for the Lagna-based house chart."}
        lagna=int(asc//30); houses=[]
        for house in range(1,13):
            sign=(lagna+house-1)%12
            planets=[p for p,data in natal.items() if ((data["sign_index"]-lagna)%12)+1==house]
            houses.append({"house":house,"sign":SIGNS[sign],"planets":planets})
        return {"houses":houses,"method":"Lagna-based sign-house map shown as a Lal Kitab reference chart; interpretive Lal Kitab rules/remedies are not inferred."}


advanced_astrology = AdvancedAstrology()
