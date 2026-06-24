import uuid
import enum

from sqlalchemy import String, Numeric, DateTime, Enum, func, Uuid
from sqlalchemy.orm import Mapped, mapped_column
from decimal import Decimal
from datetime import datetime

from app.db.base import Base

class PlanStatus(str,enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class BillingCycle(str,enum.Enum):
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"

class Plan(Base):
    __tablename__ = "plans"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(
        String(1024),
        nullable=True,
    )
    billing_cycle: Mapped[BillingCycle] = mapped_column(
        Enum(BillingCycle, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    price: Mapped[Decimal] = mapped_column(
        Numeric(12,2),
        nullable=False,
    )
    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        # default="INR",  # INR,USD,EUR,GBP,AUD etc. -> ISO 4217
    )     
    status: Mapped[PlanStatus] = mapped_column(
        Enum(PlanStatus, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=PlanStatus.ACTIVE,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )