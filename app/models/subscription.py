import uuid
import enum

from sqlalchemy import DateTime, Enum, func, Uuid, ForeignKey, Index, Date, text
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, date

from app.db.base import Base

class SubscriptionStatus(str,enum.Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    CANCELLED = "cancelled"
    EXPIRED = "expired"

class Subscription(Base):
    __tablename__ = "subscriptions"

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
    plan_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("plans.id"),
        nullable=False,
    )
    status: Mapped[SubscriptionStatus] = mapped_column(
        Enum(SubscriptionStatus, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=SubscriptionStatus.ACTIVE,
    )
    start_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )
    current_period_start: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )
    current_period_end: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )
    paused_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    resumed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    cancelled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    expired_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (
        Index(
            "ix_subscriptions_unique_active_per_customer_plan",
            "customer_id", "plan_id",
            unique=True,
            postgresql_where=text("status = 'active'"),
        ),
    )