import uuid
import enum

from sqlalchemy import String, Numeric, DateTime, Enum, func, Uuid, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from decimal import Decimal
from datetime import datetime

from app.db.base import Base

class PaymentAttemptStatus(str, enum.Enum):
    SUCCESS = "success"
    FAILED = "failed"

class PaymentAttempt(Base):
    __tablename__ = "payment_attempts"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    invoice_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("invoices.id"),
        nullable=False,
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )
    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        # default="INR",  # INR,USD,EUR,GBP,AUD etc. -> ISO 4217
    )
    status: Mapped[PaymentAttemptStatus] = mapped_column(
        Enum(PaymentAttemptStatus, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    provider_reference: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    failure_reason: Mapped[str | None] = mapped_column(
        String(1024),
        nullable=True,
    )
    idempotency_key: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        unique=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
