from fastapi import APIRouter

router = APIRouter(
    prefix="/customers",
    tags=["customers"],
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