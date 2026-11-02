import calendar
import re
from datetime import date, datetime, time, timedelta, timezone
from typing import Any, Dict, List, Optional
from zoneinfo import ZoneInfo

from .planetary_dignity import dignity_for_sign
from .transit_engine import transit_engine


SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]
SIGN_STYLES = {
    "Aries": "direct and initiative-taking", "Taurus": "steady and security-minded", "Gemini": "curious and communicative",
    "Cancer": "protective and emotionally attentive", "Leo": "warm and expressive", "Virgo": "thoughtful and practical",
    "Libra": "cooperative and fairness-seeking", "Scorpio": "private and emotionally intense", "Sagittarius": "candid and exploratory",
    "Capricorn": "measured and commitment-minded", "Aquarius": "independent and idea-led", "Pisces": "compassionate and imaginative",
}
TOPICS = ["Love", "Finance", "Career", "Wellbeing", "Spirituality"]
TOPIC_PLANETS = {
    "Love": ["Venus", "Moon", "Jupiter"],
    "Finance": ["Jupiter", "Venus", "Mercury"],
    "Career": ["Saturn", "Sun", "Mercury", "Jupiter"],
    "Wellbeing": ["Moon", "Sun", "Mars", "Saturn"],
    "Spirituality": ["Jupiter", "Ketu", "Moon", "Saturn"],
}
NATAL_FOCUS = {"Love": "Venus", "Finance": "Jupiter", "Career": "Saturn", "Wellbeing": "Moon", "Spirituality": "Jupiter"}
HOUSE_THEMES = {
    1: "self-direction", 2: "resources and speech", 3: "learning and effort", 4: "home and emotional foundations",
    5: "creativity and affection", 6: "work routines and service", 7: "partnerships", 8: "shared matters and change",
    9: "study and perspective", 10: "career and responsibility", 11: "networks and long-term aims", 12: "rest and reflection",
}
PRACTICES = {
    "Love": "choose patient, direct communication over assumptions",
    "Finance": "check costs and terms before making a commitment",
    "Career": "set one clear priority and confirm responsibilities early",
    "Wellbeing": "keep routines steady and seek qualified care for concerns",
    "Spirituality": "make room for reflection while checking impressions against facts",
}
WEEKLY_ACTIONS = {
    "Love": "Make time for an honest check-in, listen carefully, and let consistent actions matter more than passing moods.",
    "Finance": "Review a budget, compare options in writing, and avoid risking money you cannot comfortably set aside.",
    "Career": "Set a clear next step, communicate dependencies early, and record decisions and deadlines.",
    "Wellbeing": "Protect sleep and regular meals, pace demanding tasks, and seek qualified care when needed.",
    "Spirituality": "Keep one reflective practice steady and balance intuition with evidence and trusted counsel.",
}
MONTHLY_ACTIONS = {
    "Love": "Create space for shared plans without rushing labels or promises. Notice whether care is reciprocal, raise practical concerns kindly, and revisit important conversations after emotions have settled.",
    "Finance": "Use a written plan for spending, saving, and obligations. Compare significant offers carefully, leave room for unexpected costs, and seek qualified financial advice before high-stakes decisions.",
    "Career": "Choose a measurable objective and divide it into milestones. Clarify ownership with collaborators, document agreements, and review workload before accepting new responsibilities or changing direction.",
    "Wellbeing": "Treat this reading as a prompt for sustainable routines, not a health prediction. Prioritize rest, movement, and regular meals, and consult qualified clinicians about symptoms or treatment.",
    "Spirituality": "Set aside regular time for study, reflection, or service. Keep spiritual impressions grounded in lived evidence, respect personal boundaries, and revisit beliefs that create fear or pressure.",
}
TOPIC_HOUSE_MEANINGS = {
    "Love": {1: "how directly you express affection", 5: "romance, joy, and creative connection", 7: "partnership agreements and reciprocity", 11: "friendship and shared future plans", 12: "privacy, rest, and emotional boundaries"},
    "Finance": {2: "cash flow, savings, and spending habits", 5: "speculation and discretionary choices", 8: "shared money, debt, and obligations", 11: "income, gains, and long-term targets"},
    "Career": {2: "pay, practical skills, and professional communication", 6: "workload, service, and daily systems", 10: "visibility, responsibility, and career direction", 11: "professional networks and measurable gains"},
    "Wellbeing": {1: "energy, self-care, and personal pace", 4: "emotional security and your home environment", 6: "daily habits, workload, and sustainable routines", 12: "sleep, recovery, and time away from pressure"},
    "Spirituality": {5: "study, mantra, and personal practice", 8: "inner work and facing uncertainty", 9: "teachers, ethics, and wider perspective", 12: "retreat, contemplation, and release"},
}
TOPIC_HOUSE_ACTIONS = {
    "Love": {1: "show affection directly and notice where you need stronger boundaries", 5: "make room for romance and play without forcing outcomes", 7: "ask for reciprocity and state expectations before agreements", 11: "nurture friendship and shared plans; check assumptions before committing", 12: "protect privacy and name emotional needs instead of expecting others to infer them"},
    "Finance": {2: "review income, essential spending, and savings with a written plan", 5: "keep speculation and discretionary spending within limits chosen in advance", 8: "check debts, taxes, shared funds, and contract details closely", 11: "follow up on payments and opportunities while verifying payout terms", 12: "track subscriptions and hidden costs; avoid unbudgeted commitments"},
    "Career": {2: "present your skills and compensation expectations clearly", 6: "simplify routines and resolve workload bottlenecks one at a time", 10: "make work visible and clarify ownership before accepting responsibility", 11: "follow up with professional contacts and define measurable gains", 12: "complete behind-the-scenes work before announcing unfinished plans"},
    "Wellbeing": {1: "match commitments to your energy and keep a steady pace", 4: "support emotional security through a calmer home routine", 6: "make sustainable changes to daily routines", 12: "prioritize recovery and sleep; seek care for persistent symptoms"},
    "Spirituality": {5: "keep study and reflective practice regular instead of chasing signs", 8: "approach deeper questions slowly and keep practical support nearby", 9: "review teachings and values with curiosity and discernment", 12: "protect quiet time and let reflection settle before drawing conclusions"},
}
ASPECTS = {
    "Mars": {3: "4th", 6: "7th", 7: "8th"},
    "Jupiter": {4: "5th", 6: "7th", 8: "9th"},
    "Saturn": {2: "3rd", 6: "7th", 9: "10th"},
}


def word_count(text: str) -> int:
    return len(re.findall(r"\b[\w’'-]+\b", text))


class HoroscopeEngine:
    def generate(
        self,
        period: str,
        timezone_name: str,
        natal_positions: Dict[str, Dict[str, Any]],
        ascendant_sign: Optional[int],
        time_unknown: bool,
    ) -> Dict[str, Any]:
        if period not in {"daily", "tomorrow", "weekly", "monthly", "yearly"}:
            raise ValueError("Choose daily, tomorrow, weekly, monthly, or yearly")
        tz = ZoneInfo(timezone_name)
        now = datetime.now(tz)
        if period == "yearly":
            months = self._yearly_report(now, tz, natal_positions, ascendant_sign)
            overview = self._annual_overview(natal_positions, ascendant_sign)
            return {
                "period": period,
                "title": "Your year ahead",
                "date_range": f"{now.date().isoformat()} to {(now.date() + timedelta(days=365)).isoformat()}",
                "overview": overview,
                "months": months,
                "word_count": word_count(overview) + sum(item["word_count"] for item in months),
                "personalized": True,
                "method": "Current sidereal Lahiri transits compared with this birth chart; whole-sign houses when birth time is known.",
                "notice": self._notice(time_unknown),
            }

        instants = self._period_instants(now, period)
        snapshots = [
            {"at": instant, "sky": transit_engine.get_sidereal_sky(instant.astimezone(timezone.utc))}
            for instant in instants
        ]
        sections = []
        for topic in TOPICS:
            content = self._topic_reading(topic, period, snapshots, natal_positions, ascendant_sign)
            if period == "weekly":
                content = f"{content} Stay open to change."
            sections.append({"topic": topic, "content": content, "word_count": word_count(content)})
        return {
            "period": period,
            "title": {"daily": "Today", "tomorrow": "Tomorrow", "weekly": "This week", "monthly": "This month"}[period],
            "date_range": self._range_label(instants),
            "sections": sections,
            "word_count": sum(section["word_count"] for section in sections),
            "personalized": True,
            "method": "Current sidereal Lahiri transits compared with this birth chart; whole-sign houses when birth time is known.",
            "notice": self._notice(time_unknown),
        }

    def _period_instants(self, now: datetime, period: str) -> List[datetime]:
        if period == "daily":
            return [now]
        if period == "tomorrow":
            tomorrow = now + timedelta(days=1)
            return [datetime.combine(tomorrow.date(), time(12), now.tzinfo)]
        if period == "weekly":
            return [now, now + timedelta(days=3), now + timedelta(days=6)]
        month_last = calendar.monthrange(now.year, now.month)[1]
        dates = sorted({now.date(), date(now.year, now.month, max(now.day, min(15, month_last))), date(now.year, now.month, month_last)})
        return [datetime.combine(day, time(12), now.tzinfo) for day in dates]

    def _yearly_report(self, now: datetime, tz: ZoneInfo, natal: Dict[str, Dict[str, Any]], asc: Optional[int]) -> List[Dict[str, Any]]:
        results = []
        year, month = now.year, now.month
        for offset in range(12):
            absolute_month = month - 1 + offset
            year = now.year + absolute_month // 12
            month_num = absolute_month % 12 + 1
            sample_day = max(now.day, min(15, calendar.monthrange(year, month_num)[1])) if offset == 0 else 15
            instant = datetime(year, month_num, sample_day, 12, tzinfo=tz)
            sky = transit_engine.get_sidereal_sky(instant.astimezone(timezone.utc))
            monthly_focus = {topic: self._select_focus(topic, sky, natal, asc) for topic in TOPICS}
            theme_lines = []
            for topic, focus in monthly_focus.items():
                house = f", {self._ordinal(focus['house'])} house" if focus.get("house") else ""
                natal_anchor = natal.get(NATAL_FOCUS[topic], {})
                theme_lines.append(f"{topic}: {focus['planet']} in {focus['transit']['sign']}{house}; natal {NATAL_FOCUS[topic]} {natal_anchor.get('sign', 'unknown')}.")
            finance_house = monthly_focus["Finance"].get("house")
            career_house = monthly_focus["Career"].get("house")
            if finance_house and career_house:
                guidance = f"Review {HOUSE_THEMES[finance_house]} and {HOUSE_THEMES[career_house]}; verify costs and duties before commitments."
            else:
                guidance = "Use these placements as reflection prompts, verify practical details, and adjust plans to your actual circumstances."
            content = " ".join(theme_lines + [guidance])
            results.append({
                "month": instant.strftime("%B %Y"),
                "content": content,
                "word_count": word_count(content),
                "transits": {topic: {"planet": focus["planet"], "sign": focus["transit"]["sign"], "house": focus["house"]} for topic, focus in monthly_focus.items()},
            })
        return results

    def _annual_overview(self, natal: Dict[str, Dict[str, Any]], asc: Optional[int]) -> str:
        moon = natal.get("Moon", {})
        venus = natal.get("Venus", {})
        lagna = f"with {SIGNS[asc]} rising" if asc is not None else "without a calculated rising sign"
        return (
            f"This year-ahead reading is built for your {moon.get('sign', 'unknown')} Moon {lagna}. "
            f"Natal Venus is in {venus.get('sign', 'an uncalculated sign')}; the monthly notes compare Lahiri sidereal transits with your birth placements. "
            "Treat these traditional themes as reflection prompts, not fixed outcomes."
        )

    def _topic_reading(self, topic: str, period: str, snapshots: List[Dict[str, Any]], natal: Dict[str, Dict[str, Any]], asc: Optional[int]) -> str:
        focus = [self._select_focus(topic, item["sky"], natal, asc) for item in snapshots]
        first = focus[0]
        natal_planet = NATAL_FOCUS[topic]
        natal_position = natal.get(natal_planet, {})
        if period in {"daily", "tomorrow"}:
            planet = first["planet"]
            house = f" in your {self._ordinal(first['house'])} house" if first.get("house") else ""
            natal_sign = natal_position.get("sign", "an unknown sign")
            dignity = natal_position.get("dignity", "not classified").lower()
            time_label = "Tomorrow" if period == "tomorrow" else "Today"
            return f"{time_label} {planet} transits {first['transit']['sign']}{house}. Your natal {NATAL_FOCUS[topic]} is in {natal_sign}, {dignity}. {self._daily_action(topic)}"
        if period == "weekly":
            middle = focus[len(focus) // 2]
            aspect = self._aspect_sentence(middle, natal_position)
            first_house = f" through your {self._ordinal(first['house'])} house" if first.get("house") else ""
            return " ".join([
                f"This week, {first['planet']} transits {first['transit']['sign']}{first_house}, highlighting {topic.lower()} themes.",
                f"Your natal {NATAL_FOCUS[topic]} is in {natal_position.get('sign', 'an unknown sign')} ({natal_position.get('dignity', 'not classified').lower()}), shaping your personal baseline.",
                aspect or (f"The period also emphasizes {HOUSE_THEMES[middle['house']]} in your chart." if middle.get("house") else f"Your natal Moon in {natal.get('Moon', {}).get('sign', 'an unknown sign')} adds personal context."),
                WEEKLY_ACTIONS[topic],
            ])
        middle = focus[len(focus) // 2]
        last = focus[-1]
        natal_house = ((natal_position["sign_index"] - asc) % 12) + 1 if asc is not None and natal_position.get("sign_index") is not None else None
        natal_sign = natal_position.get("sign", "an unknown sign")
        dignity = natal_position.get("dignity", "not classified").lower()
        style = SIGN_STYLES.get(natal_sign, "distinctive")
        house_meaning = TOPIC_HOUSE_MEANINGS[topic].get(natal_house, HOUSE_THEMES.get(natal_house)) if natal_house else None
        if natal_house and house_meaning:
            anchor = f"Your natal {NATAL_FOCUS[topic]} in {natal_sign} ({dignity}) gives your {topic.lower()} style a {style} tone; its {self._ordinal(natal_house)} house links this theme with {house_meaning}."
        else:
            anchor = f"Your natal {NATAL_FOCUS[topic]} in {natal_sign} ({dignity}) gives your {topic.lower()} style a {style} tone, an important baseline for this month."

        def phase(focus_item: Dict[str, Any], when: datetime, label: str) -> str:
            house = focus_item.get("house")
            action = TOPIC_HOUSE_ACTIONS[topic].get(house) if house else None
            if action and house:
                return f"{label} ({when.strftime('%b %-d')}), {focus_item['planet']} in {focus_item['transit']['sign']} activates your {self._ordinal(house)} house: {action}."
            return f"{label} ({when.strftime('%b %-d')}), {focus_item['planet']} in {focus_item['transit']['sign']} emphasizes your {topic.lower()} chart themes; {PRACTICES[topic]}."

        transit_story = " ".join([
            phase(first, snapshots[0]["at"], "Early in the month"),
            phase(middle, snapshots[len(snapshots) // 2]["at"], "Midmonth"),
            phase(last, snapshots[-1]["at"], "By month-end"),
        ])
        aspect = self._aspect_sentence(middle, natal_position)
        if not aspect:
            aspect = f"Across these dates, compare the changing transit houses with your natal {NATAL_FOCUS[topic]} placement rather than treating one transit as a standalone prediction."
        return " ".join([anchor, transit_story, aspect, MONTHLY_ACTIONS[topic]])

    def _select_focus(self, topic: str, sky: Dict[str, Dict[str, Any]], natal: Dict[str, Dict[str, Any]], asc: Optional[int]) -> Dict[str, Any]:
        natal_focus = natal.get(NATAL_FOCUS[topic], {})
        natal_sign = natal_focus.get("sign_index")
        scored = []
        for order, planet in enumerate(TOPIC_PLANETS[topic]):
            transit = sky.get(planet)
            if not transit:
                continue
            house = ((transit["sign_index"] - asc) % 12) + 1 if asc is not None else None
            score = 0
            if house is not None:
                relevant_houses = {
                    "Love": {1, 5, 7, 11}, "Finance": {2, 5, 9, 11}, "Career": {2, 6, 10, 11},
                    "Wellbeing": {1, 4, 6, 12}, "Spirituality": {5, 8, 9, 12},
                }[topic]
                score += 3 if house in relevant_houses else 0
            if natal_sign is not None:
                aspect_targets = {6}
                aspect_targets.update(ASPECTS.get(planet, {}).keys())
                if (natal_sign - transit["sign_index"]) % 12 in aspect_targets:
                    score += 2
            if transit.get("retrograde") and planet in {"Mercury", "Jupiter", "Saturn"}:
                score += 1
            scored.append((score, -order, planet, transit, house))
        _, _, planet, transit, house = max(scored)
        return {"planet": planet, "transit": transit, "house": house, "natal_focus": natal_focus, "natal_planet": NATAL_FOCUS[topic]}

    def _fact_sentence(self, focus: Dict[str, Any], asc: Optional[int], at: datetime, weekly: bool = False, monthly: bool = False) -> str:
        planet, transit, house = focus["planet"], focus["transit"], focus["house"]
        sign = transit["sign"]
        if monthly:
            date_label = at.strftime("%b %-d")
            return f"Around {date_label}, transiting {planet} is in {sign}{f' and your {self._ordinal(house)} house' if house else ''}, putting its traditional themes in focus."
        if weekly:
            return f"This week, {planet} moves through {sign}{f' in your {self._ordinal(house)} house' if house else ''}, highlighting a chart-specific theme for the days ahead."
        return f"Today, {planet} is in {sign}{f' in your {self._ordinal(house)} house' if house else ''}, bringing this chart theme into focus."

    def _natal_sentence(self, topic: str, position: Dict[str, Any], weekly: bool = False) -> str:
        planet = NATAL_FOCUS[topic]
        sign = position.get("sign", "an unknown sign")
        dignity = position.get("dignity", "not calculated")
        practice = PRACTICES[topic]
        if weekly:
            return f"Your natal {planet} is in {sign} ({dignity}); {practice}, and let consistent choices matter more than a single day’s mood."
        return f"Your natal {planet} is in {sign} ({dignity}); {practice}."

    def _aspect_sentence(self, focus: Dict[str, Any], natal_position: Dict[str, Any]) -> Optional[str]:
        natal_sign = natal_position.get("sign_index")
        if natal_sign is None:
            return None
        planet = focus["planet"]
        diff = (natal_sign - focus["transit"]["sign_index"]) % 12
        aspect = ASPECTS.get(planet, {}).get(diff)
        if diff == 6:
            aspect = "7th-house"
        if not aspect:
            return None
        natal_planet = focus.get("natal_planet", "chart placements")
        return f"This transit forms a traditional {aspect} aspect to your natal {natal_planet}, linking current choices with longer-standing patterns."

    def _topic_for_planet(self, planet: str) -> str:
        return next((topic for topic, planets in TOPIC_PLANETS.items() if planet in planets), "Career")

    @staticmethod
    def _daily_action(topic: str) -> str:
        return {
            "Love": "Lead with warmth, listen closely, and avoid assuming intent.",
            "Finance": "Pause before spending; verify numbers and terms.",
            "Career": "Choose one priority and communicate your next step.",
            "Wellbeing": "Keep routines steady and make space to rest.",
            "Spirituality": "Reflect calmly and ground intuition in what you know.",
        }[topic]

    def _weekly_context(self, topic: str, focus: Dict[str, Any]) -> str:
        house = focus.get("house")
        if house:
            return f"The second half of the period keeps {HOUSE_THEMES[house]} active, so use the same measured approach if plans or conversations shift."
        return f"The Moon sign and current transits remain the changing backdrop; keep {topic.lower()} choices grounded in the facts you can confirm."

    @staticmethod
    def _ordinal(number: int) -> str:
        return {1: "1st", 2: "2nd", 3: "3rd"}.get(number, f"{number}th")

    @staticmethod
    def _range_label(instants: List[datetime]) -> str:
        if len(instants) == 1:
            return instants[0].date().isoformat()
        return f"{instants[0].date().isoformat()} to {instants[-1].date().isoformat()}"

    @staticmethod
    def _notice(time_unknown: bool) -> str:
        if time_unknown:
            return "Birth time is unknown, so house-specific wording is omitted. This is traditional astrology guidance, not a guaranteed outcome or professional advice."
        return "This is personalized traditional astrology guidance, not a guaranteed outcome or professional advice."


horoscope_engine = HoroscopeEngine()
