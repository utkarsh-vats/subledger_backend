import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.plan import Plan, PlanStatus

class PlanRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, *, name, description, billing_cycle, price, currency, status) -> Plan:
        plan = Plan(
            name=name,
            description=description,
            billing_cycle=billing_cycle,
            price=price,
            currency=currency,
            status=status,
        )
        self.session.add(plan)
        self.session.flush()
        return plan
    
    def get(self, plan_id: uuid.UUID) -> Plan | None:
        return self.session.get(Plan, plan_id)
    
    def list(self) -> list[Plan]:
        stmt = select(Plan).order_by(Plan.created_at.desc())
        return list(self.session.scalars(stmt))
    
    def update(self, plan_id: uuid.UUID, **changes) -> Plan | None:
        plan = self.get(plan_id)
        if plan is None:
            return None
        for field, value in changes.items():
            setattr(plan, field, value)
        self.session.flush()
        return plan

    def set_status(self, plan_id: uuid.UUID, status: PlanStatus) -> Plan | None:
        return self.update(plan_id, status=status)
