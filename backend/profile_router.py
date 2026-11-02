from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from pydantic import BaseModel, Field, field_validator
from datetime import date, time
from uuid import UUID
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from .database import get_session, BirthProfile, Profile
from .auth import get_current_user, User

router = APIRouter(prefix="/profile", tags=["User Profile"])

# --- SCHEMAS ---

class BirthDetailCreate(BaseModel):
    label: str = "Me"
    dob: date
    tob: time
    tob_unknown: bool = False
    birth_city: str
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    timezone: str

    @field_validator("timezone")
    @classmethod
    def validate_timezone(cls, value: str) -> str:
        try:
            ZoneInfo(value)
        except (ZoneInfoNotFoundError, ValueError):
            raise ValueError("Use a valid IANA timezone, such as Asia/Kolkata")
        return value

class BirthDetailOut(BaseModel):
    id: UUID
    label: str
    dob: date
    tob: time
    tob_unknown: bool
    birth_city: str
    latitude: float
    longitude: float
    timezone: str

class ProfileUpdate(BaseModel):
    full_name: str
    gender: str = None
    language_preference: str = "en"
    preferred_system: str = "both"

# --- ROUTES ---

@router.post("/onboard", status_code=status.HTTP_201_CREATED)
async def onboard_user(
    profile_data: ProfileUpdate,
    birth_data: BirthDetailCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # 1. Ensure user has a basic profile
    profile = session.exec(select(Profile).where(Profile.user_id == current_user.id)).first()
    if not profile:
        profile = Profile(
            user_id=current_user.id,
            full_name=profile_data.full_name,
            gender=profile_data.gender,
            language_preference=profile_data.language_preference,
            preferred_system=profile_data.preferred_system
        )
        session.add(profile)
        session.commit()
        session.refresh(profile)
    else:
        profile.full_name = profile_data.full_name
        profile.gender = profile_data.gender
        profile.language_preference = profile_data.language_preference
        profile.preferred_system = profile_data.preferred_system
        session.add(profile)
        session.commit()

    # 2. Onboarding edits the user's matching birth profile instead of adding
    # another copy. Otherwise the dashboard can keep loading an older profile
    # where the birth time was marked unknown.
    birth_profile = session.exec(
        select(BirthProfile)
        .where(
            BirthProfile.profile_id == profile.id,
            BirthProfile.label == birth_data.label,
        )
        .order_by(BirthProfile.created_at.desc())
    ).first()
    if birth_profile is None:
        birth_profile = BirthProfile(profile_id=profile.id, **birth_data.model_dump())
    else:
        for field, value in birth_data.model_dump().items():
            setattr(birth_profile, field, value)
    session.add(birth_profile)
    session.commit()
    session.refresh(birth_profile)

    return {"profile": profile, "birth_profile": birth_profile}

@router.get("/birth-profiles", response_model=List[BirthDetailOut])
async def get_birth_profiles(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    profile = session.exec(select(Profile).where(Profile.user_id == current_user.id)).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found. Please onboard first.")

    return session.exec(
        select(BirthProfile)
        .where(BirthProfile.profile_id == profile.id)
        .order_by(BirthProfile.label != "Me", BirthProfile.created_at.desc())
    ).all()

@router.post("/birth-profiles", response_model=BirthDetailOut)
async def add_birth_profile(
    birth_data: BirthDetailCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    profile = session.exec(select(Profile).where(Profile.user_id == current_user.id)).first()
    if not profile:
        raise HTTPException(status_code=404, detail="User profile not found")

    birth_profile = BirthProfile(
        profile_id=profile.id,
        **birth_data.model_dump()
    )
    session.add(birth_profile)
    session.commit()
    session.refresh(birth_profile)
    return birth_profile
