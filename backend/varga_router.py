from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from .auth import get_current_user, User
from .astrology_engine import engine
from .database import get_session, BirthProfile, Profile
from .varga_engine import SIGNS, VARGAS, varga_engine
from .planetary_dignity import dignity_for_sign

router = APIRouter(prefix="/varga", tags=["Divisional Charts"])


@router.get("/overview/{birth_profile_id}")
@router.get("/charts/{birth_profile_id}")
async def get_varga_charts(
    birth_profile_id: UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    birth_profile = session.exec(
        select(BirthProfile)
        .join(Profile, BirthProfile.profile_id == Profile.id)
        .where(BirthProfile.id == birth_profile_id, Profile.user_id == current_user.id)
    ).first()
    if not birth_profile:
        raise HTTPException(status_code=404, detail="Birth profile not found")

    dob_dt = datetime.combine(birth_profile.dob, birth_profile.tob)
    try:
        natal_positions = engine.calculate_sidereal_planetary_positions(dob_dt, birth_profile.timezone)
        jd = engine.calculate_julian_day(dob_dt, birth_profile.timezone)
        angles = None if birth_profile.tob_unknown else engine.calculate_sidereal_houses(
            jd, birth_profile.latitude, birth_profile.longitude
        )
        ascendant = angles[12] if angles else None
        charts = {}

        for varga in VARGAS:
            division = varga["division"]
            lagna_sign, lagna_degree = varga_engine.map_position(ascendant, division) if ascendant is not None else (None, None)
            placements = {}
            for name, position in natal_positions.items():
                sign_index, degree = varga_engine.map_position(position["longitude"], division)
                placements[name] = {
                    "longitude": sign_index * 30 + degree,
                    "sign_index": sign_index,
                    "sign": SIGNS[sign_index],
                    "degree": degree,
                    "house": ((sign_index - lagna_sign) % 12) + 1 if lagna_sign is not None else None,
                    "dignity": dignity_for_sign(name, sign_index),
                }
            charts[str(division)] = {
                **varga,
                "division": division,
                "planets": placements,
                "lagna_sign_index": lagna_sign,
                "lagna_sign": SIGNS[lagna_sign] if lagna_sign is not None else None,
                "lagna_degree": lagna_degree,
            }

        return {
            "profile_label": birth_profile.label,
            "charts": charts,
            "metadata": {
                "time_unknown": birth_profile.tob_unknown,
                "zodiac": "sidereal",
                "ayanamsha": "Lahiri",
                "house_system": "whole sign",
                "chart_family": "Parashari Shodashavarga",
            },
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Varga calculation error: {exc}")
