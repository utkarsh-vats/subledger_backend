import uuid

from sqlalchemy.orm import Session
from app.models.plan import Plan, PlanStatus
from app.repositories.plan import PlanRepository
from app.schemas.plan import PlanCreate, PlanUpdate
from app.exceptions import NotFoundError, ValidationError

class PlanService:
    def __init__(self, session: Session, repo: PlanRepository):
        self.session = session
        self.repo = repo

    def create(self, data: PlanCreate) -> Plan:
        required_fields = ("name", "description", "billing_cycle", "price", "currency", "status")
        data_dict = data.model_dump()
        missing_fields = [field for field in required_fields if field not in data_dict]
        if missing_fields:
            raise ValidationError(f"Missing required fields: {', '.join(missing_fields)}")
        plan = self.repo.create(**data_dict)
        self.session.commit()
        return plan
    
    def get(self, plan_id: uuid.UUID) -> Plan:
        plan = self.repo.get(plan_id)
        if plan is None:
            raise NotFoundError(f"Plan {plan_id} not found")
        return plan
    
    def list(self) -> list[Plan]:
        return self.repo.list()

    def update(self, plan_id: uuid.UUID, data: PlanUpdate) -> Plan:
        self.get(plan_id)
        changes = data.model_dump(exclude_unset=True)
        plan = self.repo.update(plan_id, **changes)
        self.session.commit()
        # already checked for None | null plan in step 1
        return plan     # type: ignore
    
    def set_status(self, plan_id: uuid.UUID, status: PlanStatus) -> Plan:
        self.get(plan_id)
        plan = self.repo.set_status(plan_id, status)
        self.session.commit()
        # already checked for None | null plan in step 1
        return plan     # type: ignore
