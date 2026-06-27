import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session
from datetime import date

from app.models.subscription import Subscription, SubscriptionStatus

class SubscriptionRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, **data) -> Subscription:
        subscription = Subscription(
            customer_id=data["customer_id"],
            plan_id=data["plan_id"],
            status=data["status"],
            start_date=data["start_date"],
            current_period_start=data["current_period_start"],
            current_period_end=data["current_period_end"],
            paused_at=data["paused_at"],
            resumed_at=data["resumed_at"],
            cancelled_at=data["cancelled_at"],
            expired_at=data["expired_at"],
        )
        self.session.add(subscription)
        self.session.flush()
        return subscription

    def get(self, subscription_id: uuid.UUID) -> Subscription | None:
        return self.session.get(Subscription, subscription_id)

    def list(self) -> list[Subscription]:
        stmt = select(Subscription).order_by(Subscription.created_at.desc())
        return list(self.session.scalars(stmt))

    def get_active_by_customer_plan(
        self, 
        customer_id: uuid.UUID,
        plan_id: uuid.UUID,        
    ) -> Subscription | None:
        stmt = (
            select(Subscription)
            .where(Subscription.customer_id == customer_id)
            .where(Subscription.plan_id == plan_id)
            .where(Subscription.status == SubscriptionStatus.ACTIVE)
        )
        return self.session.scalars(stmt).one_or_none()
    
    def list_subscriptions_by_status(self, status: SubscriptionStatus) -> list[Subscription]:
        stmt = select(Subscription).where(Subscription.status == status)
        return list(self.session.scalars(stmt))
    
    # will add method endpoint later when required
    def list_by_customer(
        self,
        customer_id: uuid.UUID,
    ) -> list[Subscription]:
        stmt = (
            select(Subscription)
            .where(Subscription.customer_id == customer_id)
        )
        return list(self.session.scalars(stmt))

    # will add method endpoint later when required
    def list_active_by_customer(
        self,
        customer_id: uuid.UUID,
    ) -> list[Subscription]:
        stmt = (
            select(Subscription)
            .where(Subscription.customer_id == customer_id)
            .where(Subscription.status == SubscriptionStatus.ACTIVE)
        )
        return list(self.session.scalars(stmt))

    # update status in service only
    def update(
        self,
        subscription_id: uuid.UUID,
        **changes
    ) -> Subscription | None:
        subscription = self.get(subscription_id)
        if subscription is None:
            return None
        for field, value in changes.items():
            setattr(subscription, field, value)     
        self.session.flush()
        return subscription

    def list_due_for_renewal(self, as_of: date | None = None) -> list[Subscription]:
        as_of = as_of or date.today()
        stmt = (
            select(Subscription)
            .where(Subscription.status == SubscriptionStatus.ACTIVE)
            .where(Subscription.current_period_end <= as_of)
            .order_by(Subscription.current_period_end.asc())
        )
        return list(self.session.scalars(stmt))