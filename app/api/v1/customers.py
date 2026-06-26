import uuid
from fastapi import APIRouter, status, Depends
from app.schemas.customer import CustomerResponse, CustomerCreate, CustomerUpdate
from app.services.customer import CustomerService
from app.api.deps import get_customer_service, get_current_admin

router = APIRouter(
    prefix="/customers",
    tags=["customers"],
)

@router.post("", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
def create_customer(
    data: CustomerCreate,
    service: CustomerService = Depends(get_customer_service),
    _: str = Depends(get_current_admin),
) -> CustomerResponse:
    # customer = service.create(data)
    return CustomerResponse.model_validate(service.create(data))

@router.get("", response_model=list[CustomerResponse], status_code=status.HTTP_200_OK)
def get_customers(
    service: CustomerService = Depends(get_customer_service),
    _: str = Depends(get_current_admin),
) -> list[CustomerResponse]:
    customers = service.list()
    return [CustomerResponse.model_validate(customer) for customer in customers]

@router.get("/{customer_id}", response_model=CustomerResponse, status_code=status.HTTP_200_OK)
def get_customer_by_id(
    customer_id: uuid.UUID,
    service: CustomerService = Depends(get_customer_service),
    _: str = Depends(get_current_admin),
):
    customer = service.get(customer_id)
    return CustomerResponse.model_validate(customer)

@router.patch("/{customer_id}")
def update_customer(
    customer_id: uuid.UUID,
    data: CustomerUpdate,
    service: CustomerService = Depends(get_customer_service),
    _: str = Depends(get_current_admin),
):
    customer = service.update(customer_id, data)
    return CustomerResponse.model_validate(customer)

@router.get("/{customer_id}/ledger")
def get_ledger_history_by_customer_id(
    customer_id: uuid.UUID,
):
    pass

@router.get("/{customer_id}/invoices")
def get_invoices_by_customer_id(
    customer_id: uuid.UUID,
):
    pass
