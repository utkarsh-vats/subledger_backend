import uuid
import enum

from sqlalchemy import String, Numeric, DateTime, Enum, func, Uuid, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from decimal import Decimal
from datetime import datetime

from app.db.base import Base

class LedgerEntryType(str, enum.Enum):
    INVOICE_CREATED = "invoice_created"
    PAYMENT_SUCCESS = "payment_success"
    PAYMENT_FAILURE = "payment_failure"

class LedgerEntry(Base):
    __tablename__ = "ledger_entries"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    customer_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("customers.id"),
        nullable=False,
    )
    invoice_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid,
        ForeignKey("invoices.id"),
        nullable=True,
    )
    entry_type: Mapped[LedgerEntryType] = mapped_column(
        Enum(LedgerEntryType, values_callable=lambda x: [e.value for e in x]),
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
    reference_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(
        String(1024),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )