from datetime import date, datetime, time
from typing import Literal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, field_validator
from sqlmodel import Session, select

from .auth import User, get_current_user
from .database import BirthProfile, Profile, get_session
from .astrology_engine import engine as astrology_engine
from .compatibility_engine import NAKSHATRAS, compare_ashtakoota

router = APIRouter(prefix="/compatibility", tags=["Compatibility"])


class PartnerBirth(BaseModel):
    full_name: str = "Partner B"
    dob: date
    tob: time = time(12, 0)
    timezone: str = "Asia/Kolkata"
    latitude: float = Field(default=28.6139, ge=-90, le=90)
    longitude: float = Field(default=77.2090, ge=-180, le=180)
    time_unknown: bool = False

    @field_validator("timezone")
    @classmethod
    def valid_timezone(cls, value: str) -> str:
        try:
            ZoneInfo(value)
        except (ZoneInfoNotFoundError, ValueError) as exc:
            raise ValueError("Use an IANA timezone such as Asia/Kolkata") from exc
        return value


class MatchRequest(BaseModel):
    partner: PartnerBirth
    scoring_order: Literal["a_bride_b_groom", "b_bride_a_groom"] = "a_bride_b_groom"


def _natal_data(birth_dt: datetime, timezone_name: str, lat: float, lon: float, time_unknown: bool) -> dict:
    positions = astrology_engine.calculate_sidereal_planetary_positions(birth_dt, timezone_name)
    moon_lon = positions["Moon"]["longitude"] % 360
    span = 360 / 27
    nak_index = min(26, int(moon_lon / span))
    pada = min(4, int((moon_lon % span) / (span / 4)) + 1)
    ascendant = None
    if not time_unknown:
        jd = astrology_engine.calculate_julian_day(birth_dt, timezone_name)
        houses = astrology_engine.calculate_sidereal_houses(jd, lat, lon)
        ascendant = int(houses[12] // 30)
    moon = {"sign_index": positions["Moon"]["sign_index"], "nakshatra_index": nak_index, "pada": pada}
    mars_sign = positions["Mars"]["sign_index"]
    trigger = {1, 2, 4, 7, 8, 12}
    references = {
        "Lagna": ((mars_sign - ascendant) % 12) + 1 if ascendant is not None else None,
        "Moon": ((mars_sign - positions["Moon"]["sign_index"]) % 12) + 1,
        "Venus": ((mars_sign - positions["Venus"]["sign_index"]) % 12) + 1,
    }
    return {"moon": moon, "moon_sign": positions["Moon"]["sign"], "nakshatra": NAKSHATRAS[nak_index], "pada": pada,
            "mars_houses": references, "mangal_flag": {key: house in trigger if house is not None else None for key, house in references.items()},
            "time_unknown": time_unknown}


@router.post("/{birth_profile_id}")
async def match_birth_profiles(
    birth_profile_id: UUID,
    payload: MatchRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    profile_a = session.exec(
        select(BirthProfile).join(Profile, BirthProfile.profile_id == Profile.id)
        .where(BirthProfile.id == birth_profile_id, Profile.user_id == current_user.id)
    ).first()
    if profile_a is None:
        raise HTTPException(status_code=404, detail="Your saved birth profile was not found")
    try:
        a_time = time(12, 0) if profile_a.tob_unknown else profile_a.tob
        b_time = time(12, 0) if payload.partner.time_unknown else payload.partner.tob
        a = _natal_data(datetime.combine(profile_a.dob, a_time), profile_a.timezone, profile_a.latitude, profile_a.longitude, profile_a.tob_unknown)
        b = _natal_data(datetime.combine(payload.partner.dob, b_time), payload.partner.timezone, payload.partner.latitude, payload.partner.longitude, payload.partner.time_unknown)
        bride, groom = (a["moon"], b["moon"]) if payload.scoring_order == "a_bride_b_groom" else (b["moon"], a["moon"])
        result = compare_ashtakoota(bride, groom)
        a["name"] = profile_a.label
        b["name"] = payload.partner.full_name
        result["orientation"] = payload.scoring_order
        bride_name, groom_name = (a["name"], b["name"]) if payload.scoring_order == "a_bride_b_groom" else (b["name"], a["name"])
        result["partners"]["a"]["name"] = bride_name
        result["partners"]["b"]["name"] = groom_name
        result["people"] = {"partner_a": {"name": a["name"], "moon_sign": a["moon_sign"], "nakshatra": a["nakshatra"], "pada": a["pada"]},
                            "partner_b": {"name": b["name"], "moon_sign": b["moon_sign"], "nakshatra": b["nakshatra"], "pada": b["pada"]}}
        result["mangal_screening"] = {"partner_a": a["mangal_flag"], "partner_b": b["mangal_flag"],
            "method": "Mars in houses 1, 2, 4, 7, 8, or 12 from Lagna, Moon, or Venus; school-specific cancellations are not applied."}
        result["notice"] = "Traditional compatibility screening for reflection. It does not establish relationship quality, consent, health, or future outcomes. Birth-time uncertainty can change Moon pada or Lagna-based screening."
        return result
    except (ValueError, IndexError) as exc:
        raise HTTPException(status_code=422, detail=f"Could not calculate this match: {exc}") from exc
