import swisseph as swe
from datetime import datetime, timezone
import pytz
from typing import Dict, Any, List, Optional

class TransitEngine:
    def __init__(self, ephe_path: str = ""):
        swe.set_ephe_path(ephe_path)

    def get_current_sky(self) -> Dict[str, Any]:
        """
        Calculates the planetary positions for the current moment (UTC).
        """
        now = datetime.utcnow()
        jd = swe.julday(now.year, now.month, now.day,
                        now.hour + now.minute/60.0 + now.second/3600.0)

        planets = {
            "Sun": swe.SUN,
            "Moon": swe.MOON,
            "Mercury": swe.MERCURY,
            "Venus": swe.VENUS,
            "Mars": swe.MARS,
            "Jupiter": swe.JUPITER,
            "Saturn": swe.SATURN,
            "Uranus": swe.URANUS,
            "Neptune": swe.NEPTUNE,
            "Pluto": swe.PLUTO,
        }

        results = {}
        for name, id in planets.items():
            res, _ = swe.calc_ut(jd, id)
            longitude = res[0]
            results[name] = {
                "longitude": longitude,
                "sign": self._get_zodiac_sign(longitude),
                "degree": longitude % 30
            }
        return results

    def get_sidereal_sky(self, moment: Optional[datetime] = None) -> Dict[str, Any]:
        """Calculate the classical grahas at a UTC instant in Lahiri sidereal zodiac."""
        instant = moment or datetime.now(timezone.utc)
        if instant.tzinfo is None:
            instant = instant.replace(tzinfo=timezone.utc)
        instant = instant.astimezone(timezone.utc)
        jd = swe.julday(
            instant.year, instant.month, instant.day,
            instant.hour + instant.minute / 60 + (instant.second + instant.microsecond / 1e6) / 3600,
        )
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
        bodies = {
            "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS,
            "Mercury": swe.MERCURY, "Jupiter": swe.JUPITER,
            "Venus": swe.VENUS, "Saturn": swe.SATURN, "Rahu": swe.MEAN_NODE,
        }
        results: Dict[str, Any] = {}
        for name, body in bodies.items():
            position, _ = swe.calc_ut(jd, body, flags)
            longitude = position[0] % 360
            results[name] = {
                "longitude": longitude,
                "sign": self._get_zodiac_sign(longitude),
                "sign_index": int(longitude // 30),
                "degree": longitude % 30,
                "speed": position[3],
                "retrograde": position[3] < 0,
            }
        ketu_longitude = (results["Rahu"]["longitude"] + 180) % 360
        results["Ketu"] = {
            "longitude": ketu_longitude,
            "sign": self._get_zodiac_sign(ketu_longitude),
            "sign_index": int(ketu_longitude // 30),
            "degree": ketu_longitude % 30,
            "speed": results["Rahu"]["speed"],
            "retrograde": results["Rahu"]["retrograde"],
        }
        return results

    def calculate_aspects(self, natal_pos: float, transit_pos: float) -> Optional[str]:
        """
        Calculates the aspect between a natal planet and a transit planet.
        """
        diff = abs(natal_pos - transit_pos)
        if diff > 180:
            diff = 360 - diff

        orb = 5.0 # Standard orb of 5 degrees

        aspects = [
            (0, "Conjunction"),
            (60, "Sextile"),
            (90, "Square"),
            (120, "Trine"),
            (180, "Opposition")
        ]

        for angle, name in aspects:
            if abs(diff - angle) <= orb:
                return name
        return None

    def _get_zodiac_sign(self, longitude: float) -> str:
        signs = [
            "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
            "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
        ]
        return signs[int(longitude / 30)]

transit_engine = TransitEngine()
