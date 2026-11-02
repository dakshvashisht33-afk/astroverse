from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from .database import get_session
from .auth import get_current_user, User
from .billing_models import SubscriptionPlan, UserSubscription, Wallet, Transaction
from typing import List
from datetime import datetime, timedelta

router = APIRouter(prefix="/billing", tags=["Billing & Payments"])

@router.get("/plans")
async def get_plans():
    # In a real app, we fetch from the database.
    # For now, we return the defined tiers from our strategy.
    return [
        {"name": "Free", "price": 0, "ai_limit": 5, "premium_reports": False},
        {"name": "Plus", "price": 9.99, "ai_limit": 100, "premium_reports": True},
        {"name": "Pro", "price": 29.99, "ai_limit": 9999, "premium_reports": True},
    ]

@router.get("/my-subscription")
async def get_my_subscription(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    sub = session.exec(select(UserSubscription).where(UserSubscription.user_id == current_user.id)).first()
    if not sub:
        return {"plan": "Free", "status": "none"}
    return {"subscription_id": sub.id, "status": sub.status, "end_date": sub.end_date}

@router.get("/wallet")
async def get_wallet_balance(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    wallet = session.exec(select(Wallet).where(Wallet.user_id == current_user.id)).first()
    if not wallet:
        # Auto-create wallet on first access
        wallet = Wallet(user_id=current_user.id)
        session.add(wallet)
        session.commit()
        session.refresh(wallet)
    return {"balance": wallet.balance, "currency": wallet.currency}
