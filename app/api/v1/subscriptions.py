from fastapi import APIRouter

router = APIRouter(
    prefix="/subscriptions",
    tags=["subscriptions"],
)

@router.post("")
def create_subscription():
    pass

@router.get("")
def get_subscriptions():
    pass

@router.get("/{subscription_id}")
def get_subscription_by_id():
    pass

@router.patch("/{subscription_id}/cancel")
def cancel_subscription_by_id():
    pass

@router.patch("/{subscription_id}/pause")
def pause_subscription_by_id():
    pass

@router.patch("/{subscription_id}/resume")
def resume_subscription_by_id():
    pass

# @router.patch("/{subscription_id}/expire")
# def expire_subscription_by_id():
#     pass
