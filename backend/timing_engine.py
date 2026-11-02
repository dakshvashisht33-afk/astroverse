from datetime import date, datetime, time, timedelta, timezone
from typing import Any, Dict, Optional
from zoneinfo import ZoneInfo

import swisseph as swe


class TimingEngine:
    """Location-specific Vedic daylight windows using Swiss Ephemeris solar events."""

    TITHIS = ["Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami", "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami", "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Purnima"]
    NAKSHATRAS = ["Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"]
    YOGAS = ["Vishkumbha", "Priti", "Ayushman", "Saubhagya", "Shobhana", "Atiganda", "Sukarma", "Dhriti", "Shula", "Ganda", "Vriddhi", "Dhruva", "Vyaghata", "Harshana", "Vajra", "Siddhi", "Vyatipata", "Variyana", "Parigha", "Shiva", "Siddha", "Sadhya", "Shubha", "Shukla", "Brahma", "Indra", "Vaidhriti"]
    KARANAS = ["Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija", "Vishti"]
    CHOGHADIYA_ORDER = ["Udveg", "Chal", "Labh", "Amrit", "Kaal", "Shubh", "Rog"]
    DAY_CHOGHADIYA_START = [0, 3, 6, 5, 2, 1, 4]  # Sunday through Saturday
    NIGHT_CHOGHADIYA_START = [5, 3, 1, 6, 4, 2, 0]

    RAHU_PART = {6: 8, 0: 2, 1: 7, 2: 5, 3: 6, 4: 4, 5: 3}  # Python weekday: Sun=6
    YAMAGANDA_PART = {6: 5, 0: 4, 1: 3, 2: 2, 3: 1, 4: 7, 5: 6}
    GULIKA_PART = {6: 7, 0: 6, 1: 5, 2: 4, 3: 3, 4: 2, 5: 1}

    def calculate_day_windows(
        self,
        lat: float,
        lon: float,
        timezone_str: str,
        on_date: Optional[date] = None,
    ) -> Dict[str, Any]:
        local_tz = ZoneInfo(timezone_str)
        local_date = on_date or datetime.now(local_tz).date()
        local_midnight = datetime.combine(local_date, time.min, tzinfo=local_tz)
        utc_midnight = local_midnight.astimezone(timezone.utc)
        start_jd = swe.julday(
            utc_midnight.year,
            utc_midnight.month,
            utc_midnight.day,
            utc_midnight.hour + utc_midnight.minute / 60 + utc_midnight.second / 3600,
        )
        geo = (lon, lat, 0.0)
        hindu_rising = swe.CALC_RISE | swe.BIT_HINDU_RISING
        hindu_setting = swe.CALC_SET | swe.BIT_HINDU_RISING
        rise_result, rise_times = swe.rise_trans(start_jd, swe.SUN, hindu_rising, geo, flags=swe.FLG_SWIEPH)
        set_result, set_times = swe.rise_trans(start_jd, swe.SUN, hindu_setting, geo, flags=swe.FLG_SWIEPH)
        if rise_result != 0 or set_result != 0:
            raise ValueError("Sunrise or sunset could not be calculated for this date and location")

        sunrise = self._julian_to_local(rise_times[0], local_tz)
        sunset = self._julian_to_local(set_times[0], local_tz)
        if sunrise.date() != local_date or sunset.date() != local_date or sunset <= sunrise:
            raise ValueError("Solar events fall outside this local date; select a location with a daily sunrise and sunset")

        daylight = (sunset - sunrise).total_seconds()
        part = daylight / 8
        weekday = local_date.weekday()

        def segment(part_number: int) -> tuple[datetime, datetime]:
            start = sunrise + timedelta(seconds=part * (part_number - 1))
            return start, start + timedelta(seconds=part)

        windows = []
        for name, kind, mapping, description in (
            ("Rahu Kaal", "caution", self.RAHU_PART, "A traditional weekday-based period calculated from local sunrise and sunset."),
            ("Yamaganda", "caution", self.YAMAGANDA_PART, "A traditional weekday-based period calculated from local daylight."),
            ("Gulika Kaal", "caution", self.GULIKA_PART, "A traditional weekday-based period calculated from local daylight."),
        ):
            start, end = segment(mapping[weekday])
            windows.append({"name": name, "type": kind, "start": self._format_datetime(start), "end": self._format_datetime(end), "description": description})

        # Abhijit is the eighth of the fifteen daytime muhurtas: one fifteenth
        # of the daylight span, centered on local apparent midday approximation.
        daylight_muhurta = daylight / 15
        midday = sunrise + timedelta(seconds=daylight / 2)
        windows.append({
            "name": "Abhijit Muhurta",
            "type": "favorable",
            "start": self._format_datetime(midday - timedelta(seconds=daylight_muhurta / 2)),
            "end": self._format_datetime(midday + timedelta(seconds=daylight_muhurta / 2)),
            "description": "The traditional midday muhurta, sized from this location’s daylight span.",
        })
        windows.sort(key=lambda item: datetime.strptime(item["start"], "%I:%M %p"))

        # Choghadiya uses eight equal segments for daylight and eight for
        # night. Calculate tomorrow's sunrise to bound the final night slot.
        next_sunrise = self._solar_event(local_date + timedelta(days=1), lat, lon, local_tz, rising=True)
        choghadiya = self._choghadiya(sunrise, sunset, next_sunrise, weekday)
        panchang = self._panchang_at_sunrise(sunrise)

        return {
            "date": local_date.isoformat(),
            "timezone": timezone_str,
            "location": {"latitude": lat, "longitude": lon},
            "solar_events": {"sunrise": self._format_datetime(sunrise), "sunset": self._format_datetime(sunset)},
            "daylight_minutes": round(daylight / 60),
            "panchang": panchang,
            "choghadiya": choghadiya,
            "approximate": False,
            "method": "Swiss Ephemeris Lahiri sidereal positions at local Hindu sunrise. Panchang limbs are sunrise snapshots; Choghadiya divides local daylight and night into eight equal weekday-specific intervals.",
            "notice": "These are traditional Panchang-style time windows, not a guarantee about an activity’s outcome.",
            "windows": windows,
        }

    @classmethod
    def _choghadiya(cls, sunrise: datetime, sunset: datetime, next_sunrise: datetime, weekday: int) -> list[dict[str, Any]]:
        result = []
        for label, start, end, sequence_start in (
            ("Day", sunrise, sunset, cls.DAY_CHOGHADIYA_START[weekday]),
            ("Night", sunset, next_sunrise, cls.NIGHT_CHOGHADIYA_START[weekday]),
        ):
            slot = (end - start).total_seconds() / 8
            for index in range(8):
                begin = start + timedelta(seconds=slot * index)
                finish = end if index == 7 else start + timedelta(seconds=slot * (index + 1))
                name = cls.CHOGHADIYA_ORDER[(sequence_start + index) % 7]
                result.append({"period": label, "name": name, "quality": "favorable" if name in {"Amrit", "Shubh", "Labh"} else "mixed" if name == "Chal" else "unfavorable", "start": cls._format_datetime(begin), "end": cls._format_datetime(finish), "date_offset": 1 if label == "Night" and finish.date() > start.date() else 0})
        return result

    @classmethod
    def _panchang_at_sunrise(cls, sunrise: datetime) -> dict[str, str]:
        utc = sunrise.astimezone(timezone.utc)
        jd = swe.julday(utc.year, utc.month, utc.day, utc.hour + utc.minute / 60 + utc.second / 3600)
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
        sun = float(swe.calc_ut(jd, swe.SUN, flags)[0][0]) % 360
        moon = float(swe.calc_ut(jd, swe.MOON, flags)[0][0]) % 360
        elongation = (moon - sun) % 360
        tithi_index = min(29, int(elongation / 12))
        paksha = "Shukla" if tithi_index < 15 else "Krishna"
        tithi_name = cls.TITHIS[tithi_index % 15]
        nakshatra = cls.NAKSHATRAS[min(26, int(moon / (360 / 27)))]
        yoga = cls.YOGAS[min(26, int(((sun + moon) % 360) / (360 / 27)))]
        karana_index = min(59, int(elongation / 6))
        if karana_index == 0:
            karana = "Kimstughna"
        elif karana_index >= 57:
            karana = {57: "Shakuni", 58: "Chatushpada", 59: "Naga"}[karana_index]
        else:
            karana = cls.KARANAS[(karana_index - 1) % 7]
        return {"weekday": sunrise.strftime("%A"), "tithi": f"{paksha} {tithi_name}", "nakshatra": nakshatra, "yoga": yoga, "karana": karana, "as_of": "Local sunrise"}

    @staticmethod
    def _solar_event(local_date: date, lat: float, lon: float, local_tz: ZoneInfo, rising: bool) -> datetime:
        local_midnight = datetime.combine(local_date, time.min, tzinfo=local_tz)
        utc_midnight = local_midnight.astimezone(timezone.utc)
        jd = swe.julday(utc_midnight.year, utc_midnight.month, utc_midnight.day, utc_midnight.hour + utc_midnight.minute / 60 + utc_midnight.second / 3600)
        event_flag = swe.CALC_RISE if rising else swe.CALC_SET
        event_flag |= swe.BIT_HINDU_RISING
        result, values = swe.rise_trans(jd, swe.SUN, event_flag, (lon, lat, 0.0), flags=swe.FLG_SWIEPH)
        if result != 0:
            raise ValueError("Next sunrise could not be calculated for this location")
        return TimingEngine._julian_to_local(values[0], local_tz)

    @staticmethod
    def _julian_to_local(julian_day: float, local_tz: ZoneInfo) -> datetime:
        year, month, day, decimal_hour = swe.revjul(julian_day, swe.GREG_CAL)
        seconds = round(decimal_hour * 3600)
        utc_dt = datetime(year, month, day, tzinfo=timezone.utc) + timedelta(seconds=seconds)
        return utc_dt.astimezone(local_tz)

    @staticmethod
    def _format_datetime(value: datetime) -> str:
        return value.strftime("%I:%M %p").lstrip("0")


timing_engine = TimingEngine()
