from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.core.security import verify_password, create_access_token
from app.core.config import settings
from app.schemas.auth import TokenResponse

router = APIRouter(
    prefix="/invoices",
)

@router.post("")            # one-time invoice - not tied to subscription
def create_invoice():
    pass

@router.post("/generate")   # invoice for subscription - subscription driven
def generate_invoice():
    pass

@router.get("/{invoice_id}")
def get_invoice_by_id():
    pass

@router.get("/{invoice_id}/ledger")
def get_invoice_ledger():
    pass