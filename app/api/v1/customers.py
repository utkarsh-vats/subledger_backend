from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.core.security import verify_password, create_access_token
from app.core.config import settings
from app.schemas.auth import TokenResponse

router = APIRouter(
    prefix="/customers",
)

@router.post("")
def create_customer():
    pass

@router.get("")
def get_customers():
    pass

@router.get("/{customer_id}")
def get_customer_by_id():
    pass

@router.get("/{customer_id}/ledger")
def get_ledger_history_by_customer_id():
    pass

@router.get("/{customer_id}/invoices")
def get_invoices_by_customer_id():
    pass