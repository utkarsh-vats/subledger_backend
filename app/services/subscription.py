import uuid

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone, timedelta
from app.models.subscription import Subscription, SubscriptionStatus
from app.repositories.subscription import SubscriptionRepository
from app.schemas.subscription import SubscriptionCreate
from app.exceptions import NotFoundError, ConflictError, ValidationError
from app.repositories.customer import CustomerRepository
from app.models.customer import CustomerStatus
from app.repositories.plan import PlanRepository
from app.models.plan import PlanStatus

# create
# get
# get list
# get list_by_status
# update status pause
# update status resume
# update status cancel
# update status expire

class SubscriptionService:
    def __init__(
        self,
        session: Session,
        repo: SubscriptionRepository,
        customer_repo: CustomerRepository,
        plan_repo: PlanRepository,
    ):
        self.session = session
        self.repo = repo
        self.customer_repo = customer_repo
        self.plan_repo = plan_repo

    def create(self, data: SubscriptionCreate) -> Subscription:
        customer = self.customer_repo.get(data.customer_id)
        if customer is None:
            raise NotFoundError(f"Customer: {data.customer_id} - not found")
        if customer.status != CustomerStatus.ACTIVE:
            raise ValidationError(f"Customer: {data.customer_id}  - is not active")
        
        plan = self.plan_repo.get(data.plan_id)
        if plan is None:
            raise NotFoundError(f"Plan: {data.plan_id} - not found")
        if plan.status != PlanStatus.ACTIVE:
            raise ValidationError(f"Plan: {data.plan_id} - is not active")
        
        existing = self.repo.get_active_by_customer_plan(
            data.customer_id,
            data.plan_id,
        )
        if existing is not None:
            raise ConflictError(f"Customer: {data.customer_id} - already has an active subscription on plan: {data.plan_id}")
        
        try:
            subscription = self.repo.create(
                customer_id=data.customer_id,
                plan_id=data.plan_id,
                status=SubscriptionStatus.ACTIVE,
                start_date=data.start_date,
                current_period_start=data.current_period_start,
                current_period_end=data.current_period_end,
                paused_at=None,
                resumed_at=None,
                cancelled_at=None,
                expired_at=None,
            )
            self.session.commit()
            return subscription
        except IntegrityError as e:
            self.session.rollback()
            raise ConflictError(f"Subscription conflict: {data.customer_id} on plan {data.plan_id}") from e
    
    def get(self, subscription_id: uuid.UUID) -> Subscription:
        subscription = self.repo.get(subscription_id)
        if subscription is None:
            raise NotFoundError(f"Subscription with id - {subscription_id} - not found")
        return subscription
    
    def list(self) -> list[Subscription]:
        return self.repo.list()
    
    # list subscriptions by status
    def list_subscription_by_status(self, status: SubscriptionStatus) -> list[Subscription]:
        return self.repo.list_subscriptions_by_status(status)

    # pause(subscription_id): only active → paused; set paused_at = now; emit subscription_paused ledger entry
    def pause_subscription(self, subscription_id: uuid.UUID) -> Subscription:
        subscription = self.get(subscription_id)
        if subscription.status != SubscriptionStatus.ACTIVE:
            raise ValidationError(f"Subscription: {subscription_id} is not active")
        subscription = self.repo.update(
            subscription_id,
            status=SubscriptionStatus.PAUSED,
            paused_at=datetime.now(timezone.utc),
        )
        assert subscription is not None
        self.session.commit()
        # emit ledger entry subscription_paused later
        return subscription

    # resume(subscription_id): only paused → active; shift current_period_end by paused duration; emit subscription_resumed
    def resume_subscription(self, subscription_id: uuid.UUID):
        subscription = self.get(subscription_id)
        if subscription.status != SubscriptionStatus.PAUSED or subscription.paused_at is None:
            raise ValidationError(f"Subscription: {subscription_id} must be paused to resume")
        resumed_at = datetime.now(timezone.utc)
        paused_duration_days = (resumed_at.date() - subscription.paused_at.date()).days
        new_period_end = subscription.current_period_end + timedelta(days=paused_duration_days)

        subscription = self.repo.update(
            subscription_id,
            status=SubscriptionStatus.ACTIVE,
            resumed_at=resumed_at,
            current_period_end=new_period_end,
        )
        assert subscription is not None
        self.session.commit()
        # emit ledger entry subscription_resumed later
        return subscription

    # cancel(subscription_id): any non-terminal → cancelled; set cancelled_at = now; emit subscription_cancelled
    def cancel_subscription(self, subscription_id: uuid.UUID):
        subscription = self.get(subscription_id)
        if subscription.status in {SubscriptionStatus.CANCELLED, SubscriptionStatus.EXPIRED}:
            raise ValidationError(f"Subscription: {subscription_id} cannot be cancelled from status {subscription.status}")
        subscription = self.repo.update(
            subscription_id,
            status=SubscriptionStatus.CANCELLED,
            cancelled_at=datetime.now(timezone.utc),
        )
        assert subscription is not None
        self.session.commit()
        # emit ledger entry subscription_cancelled later
        return subscription

