import uuid

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

from app.models.customer import CustomerStatus

class CustomerBase(BaseModel):
    name: str = Field(max_length=255)
    email: str = Field(max_length=255)
    company_name: str | None = Field(default=None, max_length=255)
    status: CustomerStatus = CustomerStatus.ACTIVE

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    email: str | None = Field(default=None, max_length=255)
    company_name: str | None = Field(default=None, max_length=255)
    status: CustomerStatus | None = None

class CustomerResponse(CustomerBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime