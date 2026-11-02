from sqlmodel import SQLModel, Field, create_engine, Session
from typing import Optional
from enum import Enum
from datetime import datetime, date, time, timezone
from uuid import UUID, uuid4
import uuid
import os
from pathlib import Path

# --- ENUMS ---
class UserRole(str, Enum):
    USER = "user"
    ASTROLOGER = "astrologer"
    EDITOR = "editor"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"

class SystemPreference(str, Enum):
    VEDIC = "vedic"
    WESTERN = "western"
    BOTH = "both"


def utcnow():
    return datetime.now(timezone.utc)

# --- MODELS ---

class User(SQLModel, table=True):
    __tablename__ = "users"
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)
    password_hash: str
    oauth_provider: Optional[str] = None
    oauth_id: Optional[str] = Field(default=None, unique=True)
    phone_number: Optional[str] = Field(default=None, unique=True)
    role: UserRole = Field(default=UserRole.USER)
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)

class Profile(SQLModel, table=True):
    __tablename__ = "profiles"
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    full_name: str
    gender: Optional[str] = None
    language_preference: str = "en"
    preferred_system: SystemPreference = Field(default=SystemPreference.BOTH)
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)

class BirthProfile(SQLModel, table=True):
    __tablename__ = "birth_profiles"
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    profile_id: UUID = Field(foreign_key="profiles.id", index=True)
    label: str = "Me"
    dob: date
    tob: time
    tob_unknown: bool = False
    birth_city: str
    latitude: float
    longitude: float
    timezone: str
    created_at: datetime = Field(default_factory=utcnow)

# --- DATABASE CONFIG ---
# In production, this would come from an environment variable
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATABASE_URL = f"sqlite:///{(PROJECT_ROOT / 'astroverse.db').as_posix()}"
DATABASE_URL = os.getenv("DATABASE_URL") or DEFAULT_DATABASE_URL
if os.getenv("RENDER") and DATABASE_URL.startswith("sqlite"):
    raise RuntimeError("Render deployment requires a persistent PostgreSQL DATABASE_URL; SQLite is ephemeral on Render.")
engine_options = {"echo": os.getenv("SQL_ECHO", "false").lower() == "true"}
if DATABASE_URL.startswith("sqlite"):
    engine_options["connect_args"] = {"check_same_thread": False}
engine = create_engine(DATABASE_URL, **engine_options)

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
