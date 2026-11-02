from fastapi import APIRouter, Depends, HTTPException, Request
from .auth import get_current_user, User
from pydantic import BaseModel


class CheckoutRequest(BaseModel):
    plan_id: str
    provider: str

router = APIRouter(prefix="/payments", tags=["Payments"])

@router.post("/create-checkout-session")
async def create_checkout(
    checkout: CheckoutRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Initiates a payment process.
    Returns a session URL or Order ID depending on the provider.
    """
    if checkout.provider not in ["stripe", "razorpay"]:
        raise HTTPException(status_code=400, detail="Unsupported payment provider")
    if checkout.plan_id not in {"plus", "pro"}:
        raise HTTPException(status_code=400, detail="Choose a paid subscription plan")

    # Never return a fabricated gateway URL: it looks actionable but cannot
    # complete a payment. Configure a real provider before enabling checkout.
    raise HTTPException(
        status_code=503,
        detail=f"{checkout.provider.capitalize()} checkout is not configured yet.",
    )

@router.post("/webhook")
async def payment_webhook(request: Request):
    """
    The endpoint that Stripe/Razorpay calls to notify us of success.
    """
    raise HTTPException(
        status_code=503,
        detail="Payment webhooks are disabled until signature verification is configured.",
    )
