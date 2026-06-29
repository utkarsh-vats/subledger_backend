import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.payment_attempt import PaymentAttempt, PaymentAttemptStatus

class PaymentAttemptRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, **data):
        pass

    def get_by_idempotency_key(self, idempotency_key: uuid.UUID) -> PaymentAttempt | None:
        pass

    def list_by_invoice(self, invoice_id: uuid.UUID) -> list[PaymentAttempt]:
        return list()
