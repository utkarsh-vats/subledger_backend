import uuid

from fastapi import APIRouter, status, Depends, Query, Header

from app.schemas.payment_attempt import PaymentAttemptResponse, PaymentAttemptCreate
from app.services.payment import PaymentService
from app.models.payment_attempt import PaymentAttemptStatus
from app.api.deps import get_payment_service, get_current_admin

router = APIRouter(
    prefix="/payments",
    tags=["payments"],
)

@router.post(
    "/record",
    response_model=PaymentAttemptResponse,
    status_code=status.HTTP_201_CREATED
)
def record_payment_attempt(
    data: PaymentAttemptCreate,
    idempotency_key: str = Header(alias="Idempotency-Key"),
    service: PaymentService = Depends(get_payment_service),
    _: str = Depends(get_current_admin),
) -> PaymentAttemptResponse:
    payment_attempt = service.record_payment(
        data=data,
        idempotency_key=idempotency_key,
    )
    return PaymentAttemptResponse.model_validate(payment_attempt)

@router.get(
    "",
    response_model=list[PaymentAttemptResponse],
    status_code=status.HTTP_200_OK
)
def list_payment_records(
    invoice_filter: uuid.UUID | None = Query(default=None, alias="invoice_id"),
    payment_status_filter: PaymentAttemptStatus | None = Query(default=None, alias="status"),
    service: PaymentService = Depends(get_payment_service),
    _: str = Depends(get_current_admin),
) -> list[PaymentAttemptResponse]:
    payment_record = service.list(
        invoice_id=invoice_filter,
        payment_status=payment_status_filter,
    )
    return [PaymentAttemptResponse.model_validate(payment_attempt) for payment_attempt in payment_record]

@router.get(
    "/{payment_attempt_id}",
    response_model=PaymentAttemptResponse,
    status_code=status.HTTP_200_OK
)
def get_payment_record(
    payment_attempt_id: uuid.UUID,
    service: PaymentService = Depends(get_payment_service),
    _: str = Depends(get_current_admin),
) -> PaymentAttemptResponse:
    payment_attempt = service.get(payment_attempt_id)
    return PaymentAttemptResponse.model_validate(payment_attempt)


