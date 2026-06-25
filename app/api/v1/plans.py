from fastapi import APIRouter

router = APIRouter(
    prefix="/plans",
    tags=["plans"],
)

@router.post("")
def create_plan():
    pass

@router.get("")
def get_plans():
    pass

@router.patch("/{plan_id}")
def update_plan():
    pass

@router.get("/{plan_id}")
def get_plan_by_id():
    pass