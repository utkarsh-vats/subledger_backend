import uuid

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import date
from decimal import Decimal

from app.repositories.invoice import InvoiceRepository
from app.schemas.invoice import InvoiceCreate
from app.models.invoice import Invoice, InvoiceType, InvoiceStatus
from app.repositories.customer import CustomerRepository
from app.models.customer import CustomerStatus
from app.repositories.subscription import SubscriptionRepository
from app.models.subscription import SubscriptionStatus
from app.exceptions import NotFoundError, ValidationError

class InvoiceService:
    def __init__(
        self,
        session: Session,
        repo: InvoiceRepository,
        customer_repo: CustomerRepository,
        subscription_repo: SubscriptionRepository,
    ):
        self.session = session
        self.repo = repo
        self.customer_repo = customer_repo
        self.subscription_repo = subscription_repo

    def create(self, data: InvoiceCreate) -> Invoice:
        if data.invoice_type == InvoiceType.SUBSCRIPTION:
            subscription = self.subscription_repo.get(data.subscription_id)
            # check if subscription exists
            if subscription is None:
                raise NotFoundError(f"Subscription: {data.subscription_id} - not found")
            # celery will issue for only active subscriptions
            # admin can generate correction invoices for paused subscriptions as well
            if subscription.status not in {SubscriptionStatus.ACTIVE, SubscriptionStatus.PAUSED}:    # status_options - active|paused|cancelled|expired
                raise ValidationError(f"Subscription: {data.subscription_id}  - is {subscription.status}")
            # get customer from subscription
            customer_id = subscription.customer_id
        
        else:
            # ONE_TIME — discriminator guarantees no subscription_id field exists
            customer_id = data.customer_id

        # customer checks
        customer = self.customer_repo.get(customer_id)
        if customer is None:
            raise NotFoundError(f"Customer: {customer_id} - not found")
        if customer.status != CustomerStatus.ACTIVE:
            raise ValidationError(f"Customer: {customer_id}  - is not active")
        
        kwargs = dict(
            customer_id=customer_id,
            invoice_type=data.invoice_type,
            amount_due=data.amount_due,
            amount_paid=Decimal("0.00"),
            currency=data.currency,
            status=InvoiceStatus.ISSUED,
            due_date=data.due_date,
            description=data.description,
        )

        if data.invoice_type == InvoiceType.SUBSCRIPTION:
            kwargs["subscription_id"] = data.subscription_id
            kwargs["period_start"] = data.period_start
            kwargs["period_end"] = data.period_end
        else:
            kwargs["subscription_id"] = None
            kwargs["period_start"] = None
            kwargs["period_end"] = None
        
        invoice = self.repo.create(**kwargs)
        self.session.commit()
        return invoice

    def get(self, invoice_id: uuid.UUID) -> Invoice:
        invoice = self.repo.get(invoice_id)
        if invoice is None:
            raise NotFoundError(f"Invoice with id - {invoice_id} - not found")
        return invoice
    
    def list(
        self,
        invoice_type: InvoiceType | None = None,
        status: InvoiceStatus | None = None,
        customer_id: uuid.UUID | None = None,
        subscription_id: uuid.UUID | None = None,
    ) -> list[Invoice]:
        return self.repo.list_invoices(
            invoice_type=invoice_type,
            status=status,
            customer_id=customer_id,
            subscription_id=subscription_id,
        )