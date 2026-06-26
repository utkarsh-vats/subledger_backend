import uuid

from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal
from datetime import datetime

from app.models.plan import BillingCycle, PlanStatus

# id - response only
# name - create + response + update(optional)
# description - optional in create + update
# billing_cycle - create + response + update(optional)
# price - create + response + update(optional) | validate gt=0
# currency - create + response + update(optional)
# status - create(ACTIVE) + Response + update(optional)
# created_at - response only
# updated_at - response only

# PlanBase
class PlanBase(BaseModel):
    name: str = Field(max_length=255)
    description: str | None = Field(default=None, max_length=1024)
    billing_cycle: BillingCycle
    price: Decimal = Field(gt=0)
    currency: str = Field(pattern=r"^[A-Z]{3}$")
    status: PlanStatus = PlanStatus.ACTIVE

# PlanCreate
class PlanCreate(PlanBase):
    pass

# PlanUpdate
class PlanUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    description: str | None = Field(default=None, max_length=1024)
    billing_cycle: BillingCycle | None = None
    price: Decimal | None = Field(default=None, gt=0)
    currency: str | None = Field(default=None, pattern=r"^[A-Z]{3}$")
    status: PlanStatus | None = None

# PlanResponse
class PlanResponse(PlanBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime