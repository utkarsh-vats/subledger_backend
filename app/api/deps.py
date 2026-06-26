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
# from app.repositories.customer import CustomerRepository
# from app.services.customer import CustomerService


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

__all__ = ["get_db", "get_current_admin", "get_plan_service", "get_customer_service"]
