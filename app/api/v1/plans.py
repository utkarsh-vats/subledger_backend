from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.core.security import verify_password, create_access_token
from app.core.config import settings
from app.schemas.auth import TokenResponse

router = APIRouter(
    prefix="/plans",
)

@router.post("")
def create_plan():
    pass

@router.get("")
def get_plans():
    pass

@router.patch("/{plan_id}")
def update_plan():
    pass

@router.get("/{plan_id}")
def get_plan_by_id():
    pass