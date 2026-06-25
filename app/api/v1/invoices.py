from fastapi import APIRouter

router = APIRouter(
    prefix="/invoices",
    tags=["invoices"],
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