from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List, Dict, Any
from .database import get_session, SQLModel, engine
from .auth import get_current_user, User
from datetime import datetime, timedelta, timezone
import random
from uuid import UUID
from .database import BirthProfile, Profile
from .astrology_engine import engine as astrology_engine
from .horoscope_engine import horoscope_engine

# --- DATABASE EXTENSION ---
# We add a table for caching horoscopes to avoid hitting AI/Calculation too often
from sqlmodel import Field


def utcnow():
    return datetime.now(timezone.utc)

class Horoscope(SQLModel, table=True):
    __tablename__ = "horoscopes"
    id: int = Field(default=None, primary_key=True)
    sign: str = Field(index=True)
    period: str # daily, weekly, monthly, yearly
    type: str # sun, moon, ascendant
    content: str
    published_at: datetime = Field(default_factory=utcnow)
    expires_at: datetime

router = APIRouter(prefix="/horoscope", tags=["Horoscopes"])


@router.get("/personalized/{birth_profile_id}/{period}")
async def get_personalized_horoscope(
    birth_profile_id: UUID,
    period: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    valid_periods = {"daily", "tomorrow", "weekly", "monthly", "yearly"}
    if period not in valid_periods:
        raise HTTPException(status_code=400, detail="Unsupported horoscope period")
    birth_profile = session.exec(
        select(BirthProfile)
        .join(Profile, BirthProfile.profile_id == Profile.id)
        .where(BirthProfile.id == birth_profile_id, Profile.user_id == current_user.id)
    ).first()
    if not birth_profile:
        raise HTTPException(status_code=404, detail="Birth profile not found")
    birth_dt = datetime.combine(birth_profile.dob, birth_profile.tob)
    natal = astrology_engine.calculate_sidereal_planetary_positions(birth_dt, birth_profile.timezone)
    houses = None
    if not birth_profile.tob_unknown:
        jd = astrology_engine.calculate_julian_day(birth_dt, birth_profile.timezone)
        houses = astrology_engine.calculate_sidereal_houses(jd, birth_profile.latitude, birth_profile.longitude)
    ascendant_sign = int(houses[12] // 30) if houses else None
    return horoscope_engine.generate(period, birth_profile.timezone, natal, ascendant_sign, birth_profile.tob_unknown)

# --- MOCK DATA GENERATOR (Until AI Phase 3 is fully integrated) ---
# In Phase 3, these will be replaced by LLM calls.
HOROSCOPE_TEMPLATES = {
    "career": ["Great opportunities arriving", "Time to focus on details", "A sudden shift in professional direction"],
    "love": ["Harmony in relationships", "Passionate encounters ahead", "Time for deep communication"],
    "health": ["Energy levels rising", "Focus on mental wellness", "Prioritize restful sleep"],
    "spirituality": ["A spiritual awakening is near", "Deepen your meditation", "Trust the cosmic flow"]
}

def generate_mock_horoscope(sign: str, period: str):
    # Simulate a personalized summary
    categories = list(HOROSCOPE_TEMPLATES.keys())
    summary = f"For {sign} ({period}): "
    details = []
    for cat in categories:
        details.append(f"**{cat.capitalize()}**: {random.choice(HOROSCOPE_TEMPLATES[cat])}")

    return summary + "\n\n" + "\n".join(details)

@router.get("/summary/{sign}/{period}")
async def get_horoscope_summary(
    sign: str,
    period: str, # weekly, monthly, yearly
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    valid_signs = {
        "aries", "taurus", "gemini", "cancer", "leo", "virgo",
        "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces",
    }
    valid_periods = {"daily", "weekly", "monthly", "yearly"}
    if sign.strip().lower() not in valid_signs:
        raise HTTPException(status_code=400, detail="Unknown zodiac sign")
    if period not in valid_periods:
        raise HTTPException(status_code=400, detail="Unsupported horoscope period")

    sign = sign.strip().title()
    # 1. Check cache first
    cached = session.exec(
        select(Horoscope).where(
            Horoscope.sign == sign,
            Horoscope.period == period,
            Horoscope.expires_at > utcnow()
        )
    ).first()

    if cached:
        return {"content": cached.content, "source": "cached"}

    # 2. Generate new summary
    content = generate_mock_horoscope(sign, period)

    # 3. Save to cache
    expiry_days = {"daily": 1, "weekly": 7, "monthly": 30, "yearly": 365}
    expiry = utcnow() + timedelta(days=expiry_days[period])
    new_horoscope = Horoscope(
        sign=sign,
        period=period,
        type="general",
        content=content,
        expires_at=expiry
    )
    session.add(new_horoscope)
    session.commit()

    return {"content": content, "source": "generated"}
