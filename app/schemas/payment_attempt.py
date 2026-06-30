import uuid

from pydantic import BaseModel, ConfigDict, Field, model_validator
from decimal import Decimal
from datetime import datetime

from app.models.payment_attempt import PaymentAttemptStatus

class PaymentAttemptBase(BaseModel):
    invoice_id: uuid.UUID
    amount: Decimal = Field(gt=0)
    currency: str = Field(pattern=r"^[A-Z]{3}$")
    status: PaymentAttemptStatus
    failure_reason: str | None = Field(default=None, max_length=1024)

class PaymentAttemptCreate(PaymentAttemptBase):
    @model_validator(mode="after")
    def failure_reason_matches_status(self):
        if self.status == PaymentAttemptStatus.SUCCESS and self.failure_reason is not None:
            raise ValueError("PaymentAttempt.failure_reason is forbidden on successful payment attempt")
        if self.status == PaymentAttemptStatus.FAILED and not self.failure_reason:
            raise ValueError("PaymentAttempt.failure_reason must be provided for failed payment attempts")
        return self

class PaymentAttemptResponse(PaymentAttemptBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    provider_reference: str | None = None
    idempotency_key: str | None = None
    created_at: datetime

