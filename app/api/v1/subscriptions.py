from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.core.security import verify_password, create_access_token
from app.core.config import settings
from app.schemas.auth import TokenResponse

router = APIRouter(
    prefix="/subscriptions",
)

@router.post("")
def create_subscription():
    pass

@router.get("")
def get_subscriptions():
    pass

@router.get("/{subscription_id}")
def get_subscription_by_id():
    pass

@router.patch("/{subscription_id}/cancel")
def cancel_subscription_by_id():
    pass

@router.patch("/{subscription_id}/pause")
def pause_subscription_by_id():
    pass

@router.patch("/{subscription_id}/resume")
def resume_subscription_by_id():
    pass

# @router.patch("/{subscription_id}/expire")
# def expire_subscription_by_id():
#     pass
