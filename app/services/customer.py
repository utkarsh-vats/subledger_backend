import uuid

from sqlalchemy.orm import Session
from app.models.customer import Customer, CustomerStatus
from app.repositories.customer import CustomerRepository
from app.schemas.customer import CustomerCreate, CustomerResponse, CustomerUpdate
from app.exceptions import NotFoundError, ValidationError


class CustomerService:
    def __init__(self, session: Session, repo: CustomerRepository):
        self.session = session
        self.repo = repo

    def create(self, data: CustomerCreate) -> Customer:
        required_fields = ("name", "email", "company_name", "status")
        data_dict = data.model_dump()
        missing_fields = [field for field in required_fields if field not in data_dict]
        if missing_fields:
            raise ValidationError(f"Missing required fields: {', '.join(missing_fields)}")
        customer = self.repo.create(**data_dict)
        self.session.commit()
        return customer

    def get(self, customer_id: uuid.UUID) -> Customer:
        customer = self.repo.get(customer_id)
        if customer is None:
            raise NotFoundError(f"Customer with id - {customer_id} - not found")
        return customer

    def list(self) -> list[Customer]:
        return self.repo.list()

    def update(self, customer_id: uuid.UUID, data: CustomerUpdate) -> Customer:
        _ = self.get(customer_id)
        changes = data.model_dump(exclude_unset=True)
        customer =  self.repo.update(customer_id, **changes)
        self.session.commit()
        # already checked for None | null plan in step 1
        return customer     # type: ignore

    def set_status(self, customer_id: uuid.UUID, status: CustomerStatus) -> Customer:
        _ = self.get(customer_id)
        customer = self.repo.set_status(customer_id, status)
        self.session.commit()
        # already checked for None | null plan in step 1
        return customer     # type: ignore