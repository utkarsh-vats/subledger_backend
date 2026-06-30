import uuid

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.schemas.payment_attempt import PaymentAttemptCreate
from app.repositories.payment_attempt import PaymentAttemptRepository
from app.models.payment_attempt import PaymentAttempt, PaymentAttemptStatus
from app.repositories.invoice import InvoiceRepository
from app.models.invoice import InvoiceStatus
from app.services.invoice import InvoiceService
# from app.services.ledger import LedgerService
# from app.models.ledger_entry import LedgerEntryType
from app.exceptions import ConflictError, ValidationError, NotFoundError

class PaymentService:
    def __init__(
        self,
        session: Session,
        repo: PaymentAttemptRepository,
        invoice_repo: InvoiceRepository,
        invoice_service: InvoiceService,
        # ledger_service: LedgerService,
    ):
        self.session = session
        self.repo = repo
        self.invoice_repo = invoice_repo
        self.invoice_service = invoice_service
        # self.ledger_service = ledger_service

    def record_payment(
        self,
        data: PaymentAttemptCreate,
        idempotency_key: str | None = None,
    ) -> PaymentAttempt:
        # header - idempotency_key: <str(uuid)>
        # data = { invoice_id, amount, currency, status, provider_reference?, failure_reason? }
        # idempotency replay check
        if idempotency_key is not None:
            existing = self.repo.get_by_idempotency_key(idempotency_key)
            if existing is not None:
                return existing
            
        # Validation - invoice
        # invoice_service handles not found exceptions itself
        invoice = self.invoice_repo.get(data.invoice_id)
        if invoice is None:
            raise NotFoundError(f"Cannot process payment for {data.invoice_id}\n - Invoice: {data.invoice_id} does not exist")
        if invoice.status not in { InvoiceStatus.ISSUED, InvoiceStatus.PARTIALLY_PAID, InvoiceStatus.OVERDUE }:
            raise ValidationError(f"Cannot process payment for '{invoice.status.value}' invoice with id {invoice.id}")
        if data.currency != invoice.currency:
            raise ValidationError(f"Cannot process payment for currency mismatch\n - invoice_currency: {invoice.currency}\n - payment_currency: {data.currency}")
        if data.status == PaymentAttemptStatus.SUCCESS:
            payable_amount = invoice.amount_due - invoice.amount_paid
            if data.amount > payable_amount:
                raise ValidationError(f"Cannot process payment due to overpayment attempt\n - max payable amount: {payable_amount}\n - amount paid: {data.amount}")

        # temporary provider_reference till payment gateway is implemented
        provider_reference = f"FAKE-{uuid.uuid4()}" if data.status == PaymentAttemptStatus.SUCCESS else None

        kwargs = dict(
            invoice_id=data.invoice_id,
            amount=data.amount,
            currency=data.currency,
            status=data.status,
            provider_reference=provider_reference,
            failure_reason=data.failure_reason,
            idempotency_key=idempotency_key,
        )

        # payment_attempt
        try:
            payment_attempt = self.repo.create(**kwargs)
        except IntegrityError as e:
            self.session.rollback()
            existing = None
            if idempotency_key is not None:
                existing = self.repo.get_by_idempotency_key(idempotency_key)
            if existing is None:
                raise ConflictError(f"Payment attempt conflict: {idempotency_key} on invoice {data.invoice_id}") from e
            return existing

        # side effects (TODO(day-5))
        if payment_attempt.status == PaymentAttemptStatus.SUCCESS:
            self.invoice_service.apply_payment(invoice, data.amount)
            # _ = self.ledger_service.create(
            #     entry_type=LedgerEntryType.PAYMENT_SUCCESS,
            #     customer_id=invoice.customer_id,
            #     invoice_id=invoice.id,
            #     amount=data.amount,
            #     currency=data.currency,
            #     reference_id=f"payment:{payment_attempt.id}",
            #     description="Payment received",
            # )
        else:
            # _ = self.ledger_service.create(
            #     entry_type=LedgerEntryType.PAYMENT_FAILURE,
            #     customer_id=invoice.customer_id,
            #     invoice_id=invoice.id,
            #     amount=data.amount,
            #     currency=data.currency,
            #     reference_id=f"payment:{payment_attempt.id}",
            #     description=data.failure_reason,
            # )
            pass
        self.session.commit()
        return payment_attempt

    def get(self, payment_attempt_id: uuid.UUID) -> PaymentAttempt:
        payment_attempt = self.repo.get(payment_attempt_id)
        if payment_attempt is None:
            raise NotFoundError(f"Payment attempt with id: {payment_attempt_id} not found")
        return payment_attempt
    
    def list(
        self,
        invoice_id: uuid.UUID | None = None,
        payment_status: PaymentAttemptStatus | None = None,
    ) -> list[PaymentAttempt]:
        return self.repo.list_payment_attempts(
            invoice_id=invoice_id,
            payment_status=payment_status,
        )








