import uuid
from fastapi import APIRouter, status, Depends
from app.schemas.plan import PlanResponse, PlanCreate, PlanUpdate
from app.services.plan import PlanService
from app.api.deps import get_plan_service, get_current_admin

router = APIRouter(
    prefix="/plans",
    tags=["plans"],
)

@router.post("", response_model=PlanResponse, status_code=status.HTTP_201_CREATED)
def create_plan(
    data: PlanCreate,
    service: PlanService = Depends(get_plan_service),
    _: str = Depends(get_current_admin),
) -> PlanResponse:
    plan = service.create(data)
    return PlanResponse.model_validate(plan)

@router.get("", response_model=list[PlanResponse], status_code=status.HTTP_200_OK)
def get_plans(
    service: PlanService = Depends(get_plan_service),
    _: str = Depends(get_current_admin),
) -> list[PlanResponse]:
    plans = service.list()
    return [PlanResponse.model_validate(plan) for plan in plans]

@router.get("/{plan_id}", response_model=PlanResponse, status_code=status.HTTP_200_OK)
def get_plan_by_id(
    plan_id: uuid.UUID,
    service: PlanService = Depends(get_plan_service),
    _: str = Depends(get_current_admin),
) -> PlanResponse:
    plan = service.get(plan_id)
    return PlanResponse.model_validate(plan)

@router.patch("/{plan_id}", response_model=PlanResponse, status_code=status.HTTP_200_OK)
def update_plan(
    plan_id: uuid.UUID,
    data: PlanUpdate,
    service: PlanService = Depends(get_plan_service),
    _: str = Depends(get_current_admin),
) -> PlanResponse:
    plan = service.update(plan_id, data)
    return PlanResponse.model_validate(plan)
