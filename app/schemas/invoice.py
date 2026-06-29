import uuid

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from typing import Annotated, Literal
from datetime import datetime, date
from decimal import Decimal

from app.models.invoice import InvoiceType, InvoiceStatus

class BaseInvoice(BaseModel):
    # id
    # subscription_id
    # customer_id
    # invoice_type
    amount_due: Decimal = Field(gt=0)
    # amount_paid
    currency: str = Field(pattern=r"^[A-Z]{3}$")
    # status
    # period_start: date | None
    # period_end: date | None
    due_date: date
    # description
    # created_at

    @field_validator("due_date")
    @classmethod
    def due_date_not_past(cls, v: date) -> date:
        if v < date.today():
            raise ValueError("Invoice.due_date cannot be in the past")
        return v

class SubscriptionInvoiceCreate(BaseInvoice):
    invoice_type: Literal[InvoiceType.SUBSCRIPTION] = InvoiceType.SUBSCRIPTION
    subscription_id: uuid.UUID
    period_start: date
    period_end: date
    description: str | None = Field(default=None, max_length=1024)

    @model_validator(mode="after")
    def check_period_order(self):
        if self.period_end <= self.period_start:
            raise ValueError("Invoice.period_end must be after Invoice.period_start")
        return self

class OneTimeInvoiceCreate(BaseInvoice):
    invoice_type: Literal[InvoiceType.ONE_TIME] = InvoiceType.ONE_TIME
    customer_id: uuid.UUID
    description: str = Field(min_length=1, max_length=1024)

InvoiceCreate = Annotated[
    SubscriptionInvoiceCreate | OneTimeInvoiceCreate,
    Field(discriminator="invoice_type"),
]

class InvoiceResponse(BaseInvoice):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    subscription_id: uuid.UUID | None = None
    customer_id: uuid.UUID
    invoice_type: InvoiceType
    # amount_due
    amount_paid: Decimal
    # currency
    status: InvoiceStatus
    period_start: date | None = None
    period_end: date | None = None
    # due_date
    description: str | None = Field(default=None, max_length=1024)
    created_at: datetime