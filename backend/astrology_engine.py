import swisseph as swe
from datetime import datetime
import pytz
from typing import Dict, Any, List
from .planetary_dignity import dignity_for_sign

class AstrologyEngine:
    def __init__(self, ephe_path: str = ""):
        # Set the path to the Swiss Ephemeris files (ephemeris files are required for high precision)
        swe.set_ephe_path(ephe_path)

    def calculate_planetary_positions(self, dob: datetime, timezone_str: str) -> Dict[str, Any]:
        """
        Calculates the longitude of major planets for a given birth time.
        """
        # Convert birth time to UTC
        local_tz = pytz.timezone(timezone_str)
        local_dt = local_tz.localize(dob)
        utc_dt = local_dt.astimezone(pytz.utc)

        # Convert UTC datetime to Julian Day
        jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day,
                        utc_dt.hour + utc_dt.minute/60.0 + utc_dt.second/3600.0)

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
            # Calculate planetary position (longitude, latitude, distance)
            res, _ = swe.calc_ut(jd, id)
            longitude = res[0]
            results[name] = {
                "longitude": longitude,
                "sign": self._get_zodiac_sign(longitude),
                "degree": longitude % 30
            }

        return results

    def calculate_julian_day(self, dob: datetime, timezone_str: str) -> float:
        """Convert a local birth datetime to the UT Julian day used by Swiss Ephemeris."""
        local_tz = pytz.timezone(timezone_str)
        local_dt = local_tz.localize(dob, is_dst=None)
        utc_dt = local_dt.astimezone(pytz.utc)
        return swe.julday(
            utc_dt.year,
            utc_dt.month,
            utc_dt.day,
            utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0,
        )

    def calculate_sidereal_planetary_positions(self, dob: datetime, timezone_str: str) -> Dict[str, Any]:
        """Calculate classical grahas in the Lahiri sidereal zodiac."""
        jd = self.calculate_julian_day(dob, timezone_str)
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
        planets = {
            "Sun": swe.SUN,
            "Moon": swe.MOON,
            "Mars": swe.MARS,
            "Mercury": swe.MERCURY,
            "Jupiter": swe.JUPITER,
            "Venus": swe.VENUS,
            "Saturn": swe.SATURN,
            "Rahu": swe.MEAN_NODE,
        }
        positions: Dict[str, Any] = {}
        for name, planet_id in planets.items():
            result, _ = swe.calc_ut(jd, planet_id, flags)
            longitude = result[0] % 360
            positions[name] = self._position_record(longitude)
            positions[name]["dignity"] = dignity_for_sign(name, int(longitude // 30))

        ketu_longitude = (positions["Rahu"]["longitude"] + 180) % 360
        positions["Ketu"] = self._position_record(ketu_longitude)
        positions["Ketu"]["dignity"] = "Not classified"
        return positions

    def calculate_sidereal_houses(self, jd: float, lat: float, lon: float) -> List[float]:
        """Return Lahiri sidereal Placidus cusps and angles for locations where Placidus is defined."""
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        cusps, ascmc = swe.houses_ex(jd, lat, lon, b"P", swe.FLG_SIDEREAL)
        return list(cusps) + [ascmc[0] % 360, ascmc[1] % 360]

    def _position_record(self, longitude: float) -> Dict[str, Any]:
        normalized = longitude % 360
        return {
            "longitude": normalized,
            "sign": self._get_zodiac_sign(normalized),
            "sign_index": int(normalized // 30),
            "degree": normalized % 30,
        }

    def _get_zodiac_sign(self, longitude: float) -> str:
        signs = [
            "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
            "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
        ]
        return signs[int(longitude / 30)]

    def calculate_houses(self, jd: float, lat: float, lon: float, hsys: bytes = b"P") -> List[float]:
        """
        Calculates the house cusps.
        """
        cusps, ascmc = swe.houses(jd, lat, lon, hsys)
        return list(cusps) + [ascmc[0], ascmc[1]] # Adding Ascendant and MC

# Singleton instance
engine = AstrologyEngine()
