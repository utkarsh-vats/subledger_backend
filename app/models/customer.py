import uuid
import enum

from sqlalchemy import String, DateTime, Enum, func, Uuid
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from app.db.base import Base

class CustomerStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )
    company_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    status: Mapped[CustomerStatus] = mapped_column(
        Enum(CustomerStatus, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=CustomerStatus.ACTIVE,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )