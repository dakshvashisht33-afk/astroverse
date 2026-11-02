from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime, timezone
from uuid import UUID, uuid4
import uuid


def utcnow():
    return datetime.now(timezone.utc)

# --- MONETIZATION MODELS ---

class SubscriptionPlan(SQLModel, table=True):
    __tablename__ = "subscription_plans"
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str # e.g., "Free", "Plus", "Pro"
    price: float
    currency: str = "USD"
    interval: str # "month", "year"
    ai_limit: int # Number of AI messages per period
    has_premium_reports: bool = False
    has_ad_free: bool = False
    created_at: datetime = Field(default_factory=utcnow)

class UserSubscription(SQLModel, table=True):
    __tablename__ = "user_subscriptions"
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    plan_id: UUID = Field(foreign_key="subscription_plans.id")
    status: str # "active", "canceled", "past_due"
    start_date: datetime = Field(default_factory=utcnow)
    end_date: datetime
    auto_renew: bool = True

class Wallet(SQLModel, table=True):
    __tablename__ = "wallets"
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", unique=True)
    balance: float = 0.0
    currency: str = "USD"
    updated_at: datetime = Field(default_factory=utcnow)

class Transaction(SQLModel, table=True):
    __tablename__ = "transactions"
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    wallet_id: UUID = Field(foreign_key="wallets.id", index=True)
    amount: float
    type: str # "credit", "debit"
    provider: str # "stripe", "razorpay", "internal"
    provider_txn_id: str
    status: str # "success", "failed", "pending"
    created_at: datetime = Field(default_factory=utcnow)
