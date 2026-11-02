from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from .database import get_session, User
from .auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user
)
from pydantic import BaseModel, EmailStr
from sqlalchemy import func

router = APIRouter(prefix="/auth", tags=["Authentication"])

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: str
    email: str
    role: str

@router.post("/signup", response_model=UserOut)
async def signup(user_in: UserCreate, session: Session = Depends(get_session)):
    normalized_email = str(user_in.email).strip().casefold()
    # Check if user exists
    existing_user = session.exec(
        select(User).where(func.lower(User.email) == normalized_email)
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create new user
    db_user = User(
        email=normalized_email,
        password_hash=get_password_hash(user_in.password),
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    normalized_email = form_data.username.strip().casefold()
    user = session.exec(
        select(User).where(func.lower(User.email) == normalized_email)
    ).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
