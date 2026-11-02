from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import Dict, Any, List
from .database import get_session, BirthProfile, Profile
from .auth import get_current_user, User
from .astrology_engine import engine
from .transit_engine import transit_engine
from .advanced_astrology import advanced_astrology
from datetime import datetime
from uuid import UUID

router = APIRouter(prefix="/chart", tags=["Astrology Charts"])


@router.get("/advanced/{birth_profile_id}")
async def get_advanced_astrology(
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
    try:
        return advanced_astrology.calculate(
            birth_profile.dob,
            birth_profile.tob,
            birth_profile.timezone,
            birth_profile.latitude,
            birth_profile.longitude,
            birth_profile.tob_unknown,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Advanced chart calculation error: {exc}") from exc

@router.get("/natal/{birth_profile_id}")
async def get_natal_chart(
    birth_profile_id: UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    birth_profile = session.exec(
        select(BirthProfile)
        .join(Profile, BirthProfile.profile_id == Profile.id)
        .where(BirthProfile.id == birth_profile_id, Profile.user_id == current_user.id)
    ).first()
    if not birth_profile:
        raise HTTPException(status_code=404, detail="Birth profile not found")

    dt_str = f"{birth_profile.dob} {birth_profile.tob}"
    dob_dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")

    try:
        planets = engine.calculate_sidereal_planetary_positions(dob_dt, birth_profile.timezone)
        jd = engine.calculate_julian_day(dob_dt, birth_profile.timezone)

        houses = None
        if not birth_profile.tob_unknown:
            houses = engine.calculate_sidereal_houses(
                jd, birth_profile.latitude, birth_profile.longitude
            )
        whole_sign_cusps = None
        if houses:
            lagna_sign = int(houses[12] // 30)
            whole_sign_cusps = [((lagna_sign + index) % 12) * 30 for index in range(12)]

        return {
            "profile_label": birth_profile.label,
            "planets": planets,
            "houses": ({
                "cusps": whole_sign_cusps,
                "ascendant": houses[12],
                "midheaven": houses[13]
            } if houses else None),
            "metadata": {
                "timezone": birth_profile.timezone,
                "city": birth_profile.birth_city,
                "time_unknown": birth_profile.tob_unknown,
                "zodiac": "sidereal",
                "ayanamsha": "Lahiri",
                "house_system": "whole sign",
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")

@router.get("/transits/{birth_profile_id}")
async def get_current_transits(
    birth_profile_id: UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # 1. Get Natal positions
    birth_profile = session.exec(
        select(BirthProfile)
        .join(Profile, BirthProfile.profile_id == Profile.id)
        .where(BirthProfile.id == birth_profile_id, Profile.user_id == current_user.id)
    ).first()
    if not birth_profile:
        raise HTTPException(status_code=404, detail="Birth profile not found")

    dt_str = f"{birth_profile.dob} {birth_profile.tob}"
    dob_dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
    natal_planets = engine.calculate_planetary_positions(dob_dt, birth_profile.timezone)

    # 2. Get Current Sky positions
    current_sky = transit_engine.get_current_sky()

    # 3. Calculate Aspects (Comparison)
    active_aspects = []
    if not birth_profile.tob_unknown:
        for p_name, p_data in current_sky.items():
            if p_name in natal_planets:
                aspect = transit_engine.calculate_aspects(
                    natal_planets[p_name]["longitude"],
                    p_data["longitude"]
                )
                if aspect:
                    active_aspects.append({
                        "planet": p_name,
                        "aspect": aspect,
                        "type": "transit_to_natal"
                    })

    return {
        "current_sky": current_sky,
        "active_aspects": active_aspects,
        "time_unknown": birth_profile.tob_unknown,
        "timestamp": datetime.utcnow().isoformat()
    }
