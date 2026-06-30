import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.payment_attempt import PaymentAttempt, PaymentAttemptStatus

class PaymentAttemptRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, **data) -> PaymentAttempt:
        payment_attempt = PaymentAttempt(
            invoice_id=data["invoice_id"],
            amount=data["amount"],
            currency=data["currency"],
            status=data["status"],
            provider_reference=data["provider_reference"],
            failure_reason=data["failure_reason"],
            idempotency_key=data["idempotency_key"],
        )
        self.session.add(payment_attempt)
        self.session.flush()
        return payment_attempt

    def get(self, payment_attempt_id: uuid.UUID) -> PaymentAttempt | None:
        return self.session.get(PaymentAttempt, payment_attempt_id)

    def get_by_idempotency_key(self, idempotency_key: str) -> PaymentAttempt | None:
        stmt = select(PaymentAttempt).where(PaymentAttempt.idempotency_key == idempotency_key)
        return self.session.scalars(stmt).one_or_none()

    def list_payment_attempts(
        self,
        invoice_id: uuid.UUID | None = None,
        payment_status: PaymentAttemptStatus | None = None,
    ) -> list[PaymentAttempt]:
        stmt = select(PaymentAttempt)
        if invoice_id is not None:
            stmt = stmt.where(PaymentAttempt.invoice_id == invoice_id)
        if payment_status is not None:
            stmt = stmt.where(PaymentAttempt.status == payment_status) 
        stmt = stmt.order_by(PaymentAttempt.created_at.desc())
        return list(self.session.scalars(stmt))
