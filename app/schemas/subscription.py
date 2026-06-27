import uuid

from pydantic import BaseModel, ConfigDict
from datetime import datetime, date

from app.models.subscription import SubscriptionStatus

class BaseSubscription(BaseModel):
    customer_id: uuid.UUID
    plan_id: uuid.UUID
    start_date: date
    current_period_start: date
    current_period_end: date

class SubscriptionCreate(BaseSubscription):
    pass

class SubscriptionResponse(BaseSubscription):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    status: SubscriptionStatus
    paused_at: datetime | None = None
    resumed_at: datetime | None = None
    cancelled_at: datetime | None = None
    expired_at: datetime | None = None
    created_at: datetime