from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import decode_token
from app.core.config import settings

from app.repositories.plan import PlanRepository
from app.services.plan import PlanService
from app.repositories.customer import CustomerRepository
from app.services.customer import CustomerService
from app.repositories.subscription import SubscriptionRepository
from app.services.subscription import SubscriptionService
from app.repositories.invoice import InvoiceRepository
from app.services.invoice import InvoiceService
from app.repositories.payment_attempt import PaymentAttemptRepository
from app.services.payment import PaymentService
# from app.services.ledger import LedgerService


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# Phase 1 - Only for admin user with hardcoded credentials
# Phase 1: single admin via env vars (POSTGRES-backed users come in Phase 2)
def get_current_admin(token: str = Depends(oauth2_scheme)) -> str:
    try:
        decoded_token_subject = decode_token(token)
    except JWTError:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Could not validate credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if decoded_token_subject != settings.ADMIN_EMAIL:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid admin user.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return decoded_token_subject

def get_plan_service(db: Session = Depends(get_db)) -> PlanService:
    return PlanService(db, PlanRepository(db))

def get_customer_service(db: Session = Depends(get_db)) -> CustomerService:
    return CustomerService(db, CustomerRepository(db))

def get_subscription_service(db: Session = Depends(get_db)) -> SubscriptionService:
    return SubscriptionService(
        db,
        SubscriptionRepository(db),
        CustomerRepository(db),
        PlanRepository(db),
    )

def get_invoice_service(db: Session = Depends(get_db)) -> InvoiceService:
    return InvoiceService(
        db,
        InvoiceRepository(db),
        CustomerRepository(db),
        SubscriptionRepository(db),
        # LedgerService(db),
    )

def get_payment_service(db: Session = Depends(get_db)):
    invoice_repo = InvoiceRepository(db)
    # ledger_service = LedgerService(db)
    invoice_service = InvoiceService(
        db,
        invoice_repo,
        CustomerRepository(db),
        SubscriptionRepository(db),
        # ledger_service,
    )
    return PaymentService(
        db,
        PaymentAttemptRepository(db),
        invoice_repo,
        invoice_service,
        # ledger_service,
    )

# def get_ledger_service():
#     pass

__all__ = [
    "get_db",
    "get_current_admin",
    "get_plan_service",
    "get_customer_service",
    "get_subscription_service",
    "get_invoice_service",
    "get_payment_service",
    # "get_ledger_service",
]
