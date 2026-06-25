from fastapi import APIRouter

router = APIRouter(
    prefix="/payments",
    tags=["payments"],
)

@router.post("/record")
def record_payment_attempt():
    pass

