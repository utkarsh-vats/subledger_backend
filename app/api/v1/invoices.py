import uuid

from fastapi import APIRouter, status, Depends, Query

from app.schemas.invoice import InvoiceResponse, InvoiceCreate, SubscriptionInvoiceCreate, OneTimeInvoiceCreate
from app.services.invoice import InvoiceService
from app.models.invoice import InvoiceStatus, InvoiceType
from app.api.deps import get_invoice_service, get_current_admin

router = APIRouter(
    prefix="/invoices",
    tags=["invoices"],
)

@router.post("", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)   # one-time invoice - not tied to subscription
def create_invoice(
    data: OneTimeInvoiceCreate,
    service: InvoiceService = Depends(get_invoice_service),
    _: str = Depends(get_current_admin),
) -> InvoiceResponse:
    invoice = service.create(data)
    return InvoiceResponse.model_validate(invoice)

@router.post("/generate", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)   # invoice for subscription - subscription driven
def generate_invoice(
    data: SubscriptionInvoiceCreate,
    service: InvoiceService = Depends(get_invoice_service),
    _: str = Depends(get_current_admin),
) -> InvoiceResponse:
    invoice = service.create(data)
    return InvoiceResponse.model_validate(invoice)

@router.get("", response_model=list[InvoiceResponse], status_code=status.HTTP_200_OK)
def list_all(
    type_filter: InvoiceType | None = Query(default=None, alias="invoice_type"),
    status_filter: InvoiceStatus | None = Query(default=None, alias="status"),
    customer_filter: uuid.UUID | None = Query(default=None, alias="customer_id"),
    subscription_filter: uuid.UUID | None = Query(default=None, alias="subscription_id"),
    service: InvoiceService = Depends(get_invoice_service),
    _: str = Depends(get_current_admin),
) -> list[InvoiceResponse]:
    invoices = service.list(
        invoice_type=type_filter,
        status=status_filter,
        customer_id=customer_filter,
        subscription_id=subscription_filter,
    )
    return [InvoiceResponse.model_validate(invoice) for invoice in invoices]


@router.get("/{invoice_id}", response_model=InvoiceResponse, status_code=status.HTTP_200_OK)
def get_invoice_by_id(
    invoice_id: uuid.UUID,
    service: InvoiceService = Depends(get_invoice_service),
    _: str = Depends(get_current_admin),
) -> InvoiceResponse:
    invoice = service.get(invoice_id)
    return InvoiceResponse.model_validate(invoice)
    

@router.get("/{invoice_id}/ledger")
def get_invoice_ledger():
    pass