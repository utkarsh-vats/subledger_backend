import uuid

from fastapi import APIRouter, status, Depends, Query

from app.schemas.subscription import SubscriptionResponse, SubscriptionCreate
from app.services.subscription import SubscriptionService
from app.models.subscription import SubscriptionStatus
from app.api.deps import get_subscription_service, get_current_admin

router = APIRouter(
    prefix="/subscriptions",
    tags=["subscriptions"],
)

@router.post("", response_model=SubscriptionResponse, status_code=status.HTTP_201_CREATED)
def create_subscription(
    data: SubscriptionCreate,
    service: SubscriptionService = Depends(get_subscription_service),
    _: str = Depends(get_current_admin),
) -> SubscriptionResponse:
    subscription = service.create(data)
    return SubscriptionResponse.model_validate(subscription)

@router.get("", response_model=list[SubscriptionResponse], status_code=status.HTTP_200_OK)
def get_subscriptions(
    status_filter: SubscriptionStatus | None = Query(default=None, alias="status"),
    service: SubscriptionService = Depends(get_subscription_service),
    _: str = Depends(get_current_admin),
) -> list[SubscriptionResponse]:
    if status_filter:
        subscriptions = service.list_subscription_by_status(status_filter)
    else:
        subscriptions = service.list()
    return [SubscriptionResponse.model_validate(subscription) for subscription in subscriptions]

@router.get("/{subscription_id}", response_model=SubscriptionResponse, status_code=status.HTTP_200_OK)
def get_subscription_by_id(
    subscription_id: uuid.UUID,
    service: SubscriptionService = Depends(get_subscription_service),
    _: str = Depends(get_current_admin),
) -> SubscriptionResponse:
    subscription = service.get(subscription_id)
    return SubscriptionResponse.model_validate(subscription)

@router.patch("/{subscription_id}/cancel", response_model=SubscriptionResponse, status_code=status.HTTP_200_OK)
def cancel_subscription_by_id(
    subscription_id: uuid.UUID,
    service: SubscriptionService = Depends(get_subscription_service),
    _: str = Depends(get_current_admin),
) -> SubscriptionResponse:
    subscription = service.cancel_subscription(subscription_id)
    return SubscriptionResponse.model_validate(subscription)

@router.patch("/{subscription_id}/pause", response_model=SubscriptionResponse, status_code=status.HTTP_200_OK)
def pause_subscription_by_id(
    subscription_id: uuid.UUID,
    service: SubscriptionService = Depends(get_subscription_service),
    _: str = Depends(get_current_admin),
) -> SubscriptionResponse:
    subscription = service.pause_subscription(subscription_id)
    return SubscriptionResponse.model_validate(subscription)

@router.patch("/{subscription_id}/resume", response_model=SubscriptionResponse, status_code=status.HTTP_200_OK)
def resume_subscription_by_id(
    subscription_id: uuid.UUID,
    service: SubscriptionService = Depends(get_subscription_service),
    _: str = Depends(get_current_admin),
) -> SubscriptionResponse:
    subscription = service.resume_subscription(subscription_id)
    return SubscriptionResponse.model_validate(subscription)

# No /expire endpoint — expiration is system-triggered via Celery beat (see DESIGN.md §5).

