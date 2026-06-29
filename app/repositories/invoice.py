import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.invoice import Invoice, InvoiceStatus, InvoiceType

class InvoiceRepository:
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, **data) -> Invoice:
        invoice = Invoice(
            subscription_id=data["subscription_id"],
            customer_id=data["customer_id"],
            invoice_type=data["invoice_type"],
            amount_due=data["amount_due"],
            amount_paid=data["amount_paid"],
            currency=data["currency"],
            status=data["status"],
            period_start=data["period_start"],
            period_end=data["period_end"],
            due_date=data["due_date"],
            description=data["description"],
        )
        self.session.add(invoice)
        self.session.flush()
        return invoice

    def get(self, invoice_id: uuid.UUID) -> Invoice | None:
        return self.session.get(Invoice, invoice_id)
    
    def list_invoices(
        self,
        invoice_type: InvoiceType | None = None,
        status: InvoiceStatus | None = None,
        customer_id: uuid.UUID | None = None,
        subscription_id: uuid.UUID | None = None,    
    ) -> list[Invoice]:
        stmt = select(Invoice)
        if invoice_type is not None:
            stmt = stmt.where(Invoice.invoice_type == invoice_type)
        if status is not None:
            stmt = stmt.where(Invoice.status == status)
        if customer_id is not None:
            stmt = stmt.where(Invoice.customer_id == customer_id)
        if subscription_id is not None:
            stmt = stmt.where(Invoice.subscription_id == subscription_id)
        stmt = stmt.order_by(Invoice.created_at.desc())
        return list(self.session.scalars(stmt))
    
    # Future methods
    # def update_amount_paid()
    
    # def update_payment_state(self, invoice_id: uuid.UUID, payment_state: InvoiceStatus) -> Invoice | None:
    #     invoice = self.get(invoice_id)
    #     if invoice is None:
    #         return None
    #     invoice.status = payment_state
    #     self.session.flush()
    #     return invoice