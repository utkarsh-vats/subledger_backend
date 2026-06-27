import uuid

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.customer import Customer, CustomerStatus
from app.repositories.customer import CustomerRepository
from app.schemas.customer import CustomerCreate, CustomerUpdate
from app.exceptions import NotFoundError, ConflictError


class CustomerService:
    def __init__(self, session: Session, repo: CustomerRepository):
        self.session = session
        self.repo = repo

    def create(self, data: CustomerCreate) -> Customer:
        existing = self.repo.get_customer_by_email(data.email)
        if existing is not None:
            raise ConflictError(f"Customer with email {data.email} already exists")
        try:
            customer = self.repo.create(**data.model_dump())
            self.session.commit()
            return customer
        except IntegrityError as e:
            self.session.rollback()
            raise ConflictError(f"Customer conflict: {data.email}") from e

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
        # already checked for None | null customer in step 1
        return customer     # type: ignore

    def set_status(self, customer_id: uuid.UUID, status: CustomerStatus) -> Customer:
        _ = self.get(customer_id)
        customer = self.repo.set_status(customer_id, status)
        self.session.commit()
        # already checked for None | null customer in step 1
        return customer     # type: ignore