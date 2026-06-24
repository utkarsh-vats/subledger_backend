import uuid
import enum

from sqlalchemy import String, Numeric, DateTime, Enum, func, Uuid, ForeignKey, Date, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column
from decimal import Decimal
from datetime import datetime, date

from app.db.base import Base

class InvoiceType(str, enum.Enum):
    SUBSCRIPTION = "subscription"
    ONE_TIME = "one_time"

class InvoiceStatus(str, enum.Enum):
    DRAFT = "draft"
    ISSUED = "issued"
    PARTIALLY_PAID = "partially_paid"
    PAID = "paid"
    OVERDUE = "overdue"
    VOID = "void"

class Invoice(Base):
    __tablename__ = "invoices"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    subscription_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid,
        ForeignKey("subscriptions.id"),
        nullable=True,
    )
    customer_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("customers.id"),
        nullable=False,
    )
    invoice_type: Mapped[InvoiceType] = mapped_column(
        Enum(InvoiceType, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    amount_due: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )
    amount_paid: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00"),
    )
    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        # default="INR",  # INR,USD,EUR,GBP,AUD etc. -> ISO 4217
    )
    status: Mapped[InvoiceStatus] = mapped_column(
        Enum(InvoiceStatus, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=InvoiceStatus.ISSUED
    )
    period_start: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )
    period_end: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )
    due_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(
        String(1024),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint(
            "(invoice_type = 'subscription' AND subscription_id IS NOT NULL "
            "AND period_start IS NOT NULL AND period_end IS NOT NULL) "
            "OR "
            "(invoice_type = 'one_time' AND subscription_id IS NULL "
            "AND period_start IS NULL AND period_end IS NULL "
            "AND description IS NOT NULL)",
            name="ck_invoice_type_consistency",
        ),
    )