from fastapi import HTTPException, status
from .billing_models import UserSubscription, SubscriptionPlan
from sqlmodel import Session, select
from uuid import UUID
from datetime import datetime, timezone

async def check_premium_access(user_id: UUID, session: Session, feature: str):
    """
    Universal paywall check.
    Returns True if user has access, otherwise raises 402 Payment Required.
    """
    # 1. Check for active subscription
    sub = session.exec(
        select(UserSubscription).where(UserSubscription.user_id == user_id)
    ).first()

    # If no subscription, they are 'Free'
    now = datetime.now(timezone.utc)
    end_date = sub.end_date if sub else None
    if end_date and end_date.tzinfo is None:
        end_date = end_date.replace(tzinfo=timezone.utc)
    if not sub or sub.status != "active" or end_date <= now:
        # Free users might have limited access
        if feature == "ai_chat":
            # In a real app, we'd count messages in the ai_messages table
            # For this MVP, we'll allow a few messages before blocking
            return True

        if feature == "premium_report":
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="This report requires a Plus or Pro subscription."
            )

        return True

    # 2. If they have a subscription, check the plan limits
    plan = session.get(SubscriptionPlan, sub.plan_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="An active subscription plan is required for this feature.",
        )

    if feature == "premium_report" and not plan.has_premium_reports:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Your current plan does not include premium reports."
        )

    return True
