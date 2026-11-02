from fastapi import APIRouter, Depends, HTTPException
from .database import get_session, Profile
from .auth import get_current_user, User
from .timing_engine import timing_engine
from .database import BirthProfile
from sqlmodel import Session, select

router = APIRouter(prefix="/timing", tags=["Cosmic Timing"])

@router.get("/daily")
async def get_daily_timing(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Get the user's birth profile for location data
    profile = session.exec(
        select(BirthProfile)
        .join(Profile, BirthProfile.profile_id == Profile.id)
        .where(Profile.user_id == current_user.id)
        .order_by(BirthProfile.label != "Me", BirthProfile.created_at.desc())
    ).first()
    if not profile:
        # Fallback to default coordinates if no profile exists
        lat, lon, tz = 28.6139, 77.2090, "Asia/Kolkata"
    else:
        lat, lon, tz = profile.latitude, profile.longitude, profile.timezone

    try:
        return timing_engine.calculate_day_windows(lat, lon, tz)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
