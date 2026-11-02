from math import isfinite
from typing import Any, Dict, List, Tuple


SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

# The traditional Shodashavarga set. Several additional varga schemes exist;
# this set uses the standard Parashari sign-start rules for each division.
VARGAS = [
    {"division": 1, "name": "Rashi", "brief": "D1 · Birth chart and whole-sign houses."},
    {"division": 2, "name": "Hora", "brief": "D2 · Hora chart."},
    {"division": 3, "name": "Drekkana", "brief": "D3 · Drekkana chart."},
    {"division": 4, "name": "Chaturthamsa", "brief": "D4 · Chaturthamsa chart."},
    {"division": 7, "name": "Saptamsa", "brief": "D7 · Saptamsa chart."},
    {"division": 9, "name": "Navamsa", "brief": "D9 · Navamsa chart."},
    {"division": 10, "name": "Dasamsa", "brief": "D10 · Dasamsa chart."},
    {"division": 12, "name": "Dwadashamsa", "brief": "D12 · Dwadashamsa chart."},
    {"division": 16, "name": "Shodashamsa", "brief": "D16 · Shodashamsa chart."},
    {"division": 20, "name": "Vimsamsa", "brief": "D20 · Vimsamsa chart."},
    {"division": 24, "name": "Chaturvimsamsa", "brief": "D24 · Chaturvimsamsa chart."},
    {"division": 27, "name": "Saptavimsamsa", "brief": "D27 · Saptavimsamsa chart."},
    {"division": 30, "name": "Trimsamsa", "brief": "D30 · Unequal Parashari Trimsamsa segments."},
    {"division": 40, "name": "Khavedamsa", "brief": "D40 · Khavedamsa chart."},
    {"division": 45, "name": "Akshavedamsa", "brief": "D45 · Akshavedamsa chart."},
    {"division": 60, "name": "Shashtiamsa", "brief": "D60 · Shashtiamsa chart."},
]


class VargaEngine:
    """Parashari Shodashavarga placement calculations for sidereal longitudes."""

    def calculate_varga_position(self, longitude: float, division: int) -> float:
        """Return a varga longitude using that division's sign and segment rules."""
        sign_index, degree = self.map_position(longitude, division)
        return sign_index * 30 + degree

    def map_position(self, longitude: float, division: int) -> Tuple[int, float]:
        if not isfinite(longitude):
            raise ValueError("Longitude must be a finite number")
        if division not in {item["division"] for item in VARGAS}:
            raise ValueError(f"Unsupported Shodashavarga division: D{division}")

        longitude %= 360
        natal_sign = int(longitude // 30)
        degree = longitude % 30
        if division == 1:
            return natal_sign, degree

        if division == 30:
            return self._trimsamsa(natal_sign, degree)

        part_size = 30.0 / division
        part = min(division - 1, int(degree / part_size))
        fraction = (degree - part * part_size) / part_size

        if division == 2:
            # Odd signs: Leo then Cancer. Even signs: Cancer then Leo.
            target_sign = (4 if part == 0 else 3) if natal_sign % 2 == 0 else (3 if part == 0 else 4)
        elif division == 3:
            target_sign = (natal_sign + part * 4) % 12
        elif division == 4:
            target_sign = (natal_sign + part * 3) % 12
        elif division == 7:
            start = natal_sign if natal_sign % 2 == 0 else (natal_sign + 6) % 12
            target_sign = (start + part) % 12
        elif division == 9:
            modality_start = {0: natal_sign, 1: natal_sign + 8, 2: natal_sign + 4}[natal_sign % 3]
            target_sign = (modality_start + part) % 12
        elif division == 10:
            start = natal_sign if natal_sign % 2 == 0 else natal_sign + 8
            target_sign = (start + part) % 12
        elif division == 12:
            target_sign = (natal_sign + part) % 12
        elif division == 16:
            start = {0: 0, 1: 4, 2: 8}[natal_sign % 3]
            target_sign = (start + part) % 12
        elif division == 20:
            start = {0: 0, 1: 8, 2: 4}[natal_sign % 3]
            target_sign = (start + part) % 12
        elif division == 24:
            start = 4 if natal_sign % 2 == 0 else 3
            target_sign = (start + part) % 12
        elif division == 27:
            element_start = {0: 0, 1: 3, 2: 6, 3: 9}[natal_sign % 4]
            target_sign = (element_start + part) % 12
        elif division == 40:
            start = 0 if natal_sign % 2 == 0 else 6
            target_sign = (start + part) % 12
        elif division == 45:
            start = {0: 0, 1: 4, 2: 8}[natal_sign % 3]
            target_sign = (start + part) % 12
        elif division == 60:
            start = 0 if natal_sign % 2 == 0 else 6
            target_sign = (start + part) % 12
        else:
            raise ValueError(f"Unsupported Shodashavarga division: D{division}")

        return target_sign % 12, min(fraction * 30.0, 29.999999999)

    def _trimsamsa(self, natal_sign: int, degree: float) -> Tuple[int, float]:
        if natal_sign % 2 == 0:
            segments = [(5, 0), (5, 10), (8, 8), (7, 2), (5, 6)]
        else:
            segments = [(5, 1), (7, 5), (8, 11), (5, 9), (5, 7)]
        start = 0.0
        for width, target_sign in segments:
            if degree < start + width:
                within_segment = (degree - start) / width
                return target_sign, min(within_segment * 30.0, 29.999999999)
            start += width
        width, target_sign = segments[-1]
        return target_sign, min(((degree - start) / width) * 30.0, 29.999999999)

    def get_varga_brief(self, division: int) -> str:
        item = next((v for v in VARGAS if v["division"] == division), None)
        return item["brief"] if item else f"D{division} divisional chart."

    def get_all_vargas_for_planet(self, planet_name: str, longitude: float) -> List[Dict[str, Any]]:
        results = []
        for varga in VARGAS:
            sign_index, degree = self.map_position(longitude, varga["division"])
            results.append({
                **varga,
                "planet": planet_name,
                "longitude": sign_index * 30 + degree,
                "sign_index": sign_index,
                "sign": SIGNS[sign_index],
                "degree": degree,
            })
        return results


varga_engine = VargaEngine()
