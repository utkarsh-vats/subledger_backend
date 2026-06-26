import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.customer import Customer, CustomerStatus

class CustomerRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, **data) -> Customer:
        customer = Customer(
            name=data["name"],
            email=data["email"],
            company_name=data["company_name"],
            status=data["status"],
        )
        self.session.add(customer)
        self.session.flush()
        return customer

    def get(self, customer_id: uuid.UUID) -> Customer | None:
        return self.session.get(Customer, customer_id)

    def list(self) -> list[Customer]:
        stmt = select(Customer).order_by(Customer.created_at.desc())
        return list(self.session.scalars(stmt))

    def update(self, customer_id: uuid.UUID, **changes) -> Customer | None:
        customer = self.get(customer_id)
        if customer is None:
            return None
        for field, value in changes.items():
            setattr(customer, field, value)
        self.session.flush()
        return customer

    def set_status(self, customer_id: uuid.UUID, status: CustomerStatus):
        return self.update(customer_id, status=status)