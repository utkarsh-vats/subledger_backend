import uuid
import random
from fastapi import status
from app.models.invoice import InvoiceStatus, InvoiceType

URL_SUBSCRIPTIONS_BASE = "/api/v1/subscriptions"
URL_CUSTOMERS_BASE = "/api/v1/customers"
URL_PLANS_BASE = "/api/v1/plans"
URL_INVOICE_BASE = "/api/v1/invoices"

def _create_customer(client, auth_header, **overrides):
    payload = {
        "name": "test-customer",
        "email": "testcustomer@subledger.local",
        "company_name": "subledget_local",
        "status": "active",
    }
    payload.update(overrides)
    response = client.post(
        URL_CUSTOMERS_BASE,
        json=payload,
        headers=auth_header,
    )
    assert response.status_code == status.HTTP_201_CREATED, f"Expected 201 for _create_customer, got {response.status_code}: {response.text}"
    return response.json()

def _create_plan(client, auth_header, **overrides):
    payload = {
        "name": "test-plan",
        "description": "test plan for tests",
        "billing_cycle": "monthly",
        "price": 100.0,
        "currency": "INR",
        "status": "active"
    }
    payload.update(overrides)
    response = client.post(
        URL_PLANS_BASE,
        json=payload,
        headers=auth_header,
    )
    assert response.status_code == status.HTTP_201_CREATED, f"Expected 201 for _create_plan, got {response.status_code}: {response.text}"
    return response.json()

def _create_subscription(client, auth_header, **overrides):
    if "customer_id" not in overrides:
        customer = _create_customer(client, auth_header)
        overrides["customer_id"] = customer["id"]

    if "plan_id" not in overrides:
        plan = _create_plan(client, auth_header)
        overrides["plan_id"] = plan["id"]

    payload = {
        "customer_id": overrides["customer_id"],
        "plan_id": overrides["plan_id"],
        "start_date": "2026-06-27",
        "current_period_start": "2026-06-27",
        "current_period_end": "2036-06-27"
    }
    payload.update(overrides)
    response = client.post(
        URL_SUBSCRIPTIONS_BASE,
        json=payload,
        headers=auth_header,
    )
    assert response.status_code == status.HTTP_201_CREATED, f"Expected 201 for _create_subscription, got {response.status_code}: {response.text}"
    return response.json()

def _create_invoice(
    client,
    auth_header = None,
    type:InvoiceType = InvoiceType.ONE_TIME,
    **overrides
):
    if type == InvoiceType.SUBSCRIPTION:
        if "subscription_id" not in overrides:
            subscription = _create_subscription(client, auth_header)
            overrides["subscription_id"] = subscription["id"]
        else:
            pass
        if "period_start" not in overrides:
            overrides["period_start"] = "2026-06-28"
        if "period_end" not in overrides:
            overrides["period_end"] = "2026-06-30"
    else:
        if "customer_id" not in overrides:
            customer = _create_customer(client, auth_header)
            overrides["customer_id"] = customer['id']

    if "description" not in overrides:
        overrides["description"] = ""

    if type == InvoiceType.SUBSCRIPTION:
        payload = {
            "subscription_id": overrides["subscription_id"],
            "invoice_type": type.value,
            "amount_due": 1200.0,
            "currency": "INR",
            "due_date": "2026-07-05",
        }
        URL_CREATE_INVOICE = f"{URL_INVOICE_BASE}/generate"
    else:
        payload = {
            "customer_id":overrides["customer_id"],
            "invoice_type": type.value,
            "amount_due": 1200.0,
            "currency": "INR",
            "due_date": "2026-07-05",
        }
        URL_CREATE_INVOICE = URL_INVOICE_BASE

    payload.update(overrides)
    invoice = client.post(
        URL_CREATE_INVOICE,
        json=payload,
        headers=auth_header,
    )
    return invoice

def test_create_invoice_unauthorized(client, auth_header):
    customer = _create_customer(client, auth_header)
    response = _create_invoice(client, customer_id=customer['id'])
    assert response.status_code == status.HTTP_401_UNAUTHORIZED, f"Expected 401, got {response.status_code}: {response.text}"

def test_create_one_time_invoice_authorized(client, auth_header):
    response = _create_invoice(
        client,
        auth_header,
        type=InvoiceType.ONE_TIME,
        description="test_one_time_invoice",
    )
    body = response.json()
    assert response.status_code == status.HTTP_201_CREATED, f"Expected 201, got {response.status_code}: {response.text}"
    assert body['subscription_id'] is None, f"Expected no subscription for one time invoice - {response.text}"
    assert body['period_start'] is None, f"Expected no start period for one time invoice - {response.text}"
    assert body['period_end'] is None, f"Expected no end period for one time invoice - {response.text}"
    assert body['status'] == InvoiceStatus.ISSUED, f"Expected Invoice.status = issued, got {body['status']} - {response.text}"
    assert len(body['currency']) == 3, f"Expected an ISO 4217 value for currency, got {body['currency']} - {response.text}"
    assert len(body['description']) in range(1, 1024), f"Expected a valid description, got {body['description']} - {response.text}"

def test_create_subscription_invoice_authorized(client, auth_header):
    response = _create_invoice(
        client,
        auth_header,
        type=InvoiceType.SUBSCRIPTION,
    )
    body = response.json()
    assert response.status_code == status.HTTP_201_CREATED, f"Expected 201, got {response.status_code}: {response.text}"
    assert body['subscription_id'] is not None, f"Expected subscription for subscription invoice - {response.text}"
    assert body['customer_id'] is not None, f"Expected customer for subscription invoice - {response.text}"
    assert body['period_start'] < body['period_end'], f"Expecter Invoice.period_end to be later than Invoice.period_start\n - period_start: {body['period_start']}\n - period_end: {body['period_end']}\n - {response.text}"
    assert body['status'] == InvoiceStatus.ISSUED, f"Expected Invoice.status = issued, got {body['status']} - {response.text}"
    assert len(body['currency']) == 3, f"Expected an ISO 4217 value for currency, got {body['currency']} - {response.text}"
    assert len(body['description']) in range(0, 1024), f"Expected a valid description, got {body['description']} - {response.text}"

def test_create_one_time_invoice_missing_customer(client, auth_header):
    response = _create_invoice(
        client,
        auth_header,
        type=InvoiceType.ONE_TIME,
        customer_id=str(uuid.uuid4()),
        description="test_one_time_invoice",
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND, f"Expected 404, got {response.status_code}: {response.text}"

def test_create_one_time_invoice_invalid_customer(client, auth_header):
    response = _create_invoice(
        client,
        auth_header,
        type=InvoiceType.ONE_TIME,
        customer_id="a_random_string_passed_as_customer_id",
        description="test_one_time_invoice",
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT, f"Expected 422, got {response.status_code}: {response.text}"

def test_create_subscription_invoice_missing_subscription(client, auth_header):
    response = _create_invoice(
        client,
        auth_header,
        type=InvoiceType.SUBSCRIPTION,
        subscription_id=f"{uuid.uuid4()}",
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND, f"Expected 404, got {response.status_code}: {response.text}"

def test_create_subscription_invoice_invalid_subscription(client, auth_header):
    response = _create_invoice(
        client,
        auth_header,
        type=InvoiceType.SUBSCRIPTION,
        subscription_id="a_random_string_passed_as_customer_id",
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT, f"Expected 422, got {response.status_code}: {response.text}"

def test_create_invoice_with_past_due_date(client, auth_header):
    invoice_type = random.choice(list(InvoiceType))
    response = _create_invoice(
        client,
        auth_header,
        type=invoice_type,
        due_date="2020-10-10",
        description="test invoice",
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT, f"Expected status 422, got {response.status_code}: {response.text}"

def test_create_subscription_invoice_with_inverted_period(client, auth_header):
    response = _create_invoice(
        client,
        auth_header,
        type=InvoiceType.SUBSCRIPTION,
        period_start="2026-06-28",
        period_end="2026-06-28",
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT, f"Expected status 422, got {response.status_code}: {response.text}"

def test_get_unknown_invoice(client, auth_header):
    response = client.get(
        f"{URL_INVOICE_BASE}/{uuid.uuid4()}",
        headers=auth_header,
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND, f"Expected status 404, got {response.status_code}: {response.text}"
    
def test_get_invoice_by_id(client, auth_header):
    invoice_type = random.choice(list(InvoiceType))
    invoice = _create_invoice(
        client,
        auth_header,
        type=invoice_type,
        description="test invoice",
    )
    response = client.get(
        f"{URL_INVOICE_BASE}/{invoice.json()['id']}",
        headers=auth_header,
    )
    assert response.status_code == status.HTTP_200_OK, f"Expected status 200, got {response.status_code}: {response.text}"
    
def test_get_invoice_without_jwt(client, auth_header):
    invoice_type = random.choice(list(InvoiceType))
    invoice = _create_invoice(
        client,
        auth_header,
        type=invoice_type,
        description="test invoice",
    )
    response = client.get(
        f"{URL_INVOICE_BASE}/{invoice.json()['id']}",
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED, f"Expected status 401, got {response.status_code}: {response.text}"

def test_create_one_time_invoice_on_inactive_customer(client, auth_header):
    customer = _create_customer(client, auth_header)
    _ = client.patch(
        f"{URL_CUSTOMERS_BASE}/{customer['id']}",
        json={
            "status": "inactive",
        },
        headers=auth_header,
    )
    response = _create_invoice(
        client,
        auth_header,
        type=InvoiceType.ONE_TIME,
        customer_id=customer['id'],
        description="test invoice",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST, f"Expected status 400, got {response.status_code}: {response.text}"

def test_create_subscription_invoice_on_inactive_customer(client, auth_header):
    customer = _create_customer(client, auth_header)
    subscription = _create_subscription(client, auth_header, customer_id=customer['id'])
    _ = client.patch(
        f"{URL_CUSTOMERS_BASE}/{customer['id']}",
        json={
            "status": "inactive",
        },
        headers=auth_header,
    )
    response = _create_invoice(
        client,
        auth_header,
        type=InvoiceType.SUBSCRIPTION,
        subscription_id=subscription['id'],
        description="test invoice",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST, f"Expected status 400, got {response.status_code}: {response.text}"

def test_create_subscription_invoice_on_cancelled_subscription(client, auth_header):
    subscription = _create_subscription(client, auth_header)
    _ = client.patch(
        f"{URL_SUBSCRIPTIONS_BASE}/{subscription['id']}/cancel",
        headers=auth_header,
    )
    response = _create_invoice(
        client,
        auth_header,
        type=InvoiceType.SUBSCRIPTION,
        subscription_id=subscription['id'],
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST, f"Expected status 400, got {response.status_code}: {response.text}"

def test_create_subscription_invoice_on_paused_subscription(client, auth_header):
    subscription = _create_subscription(client, auth_header)
    _ = client.patch(
        f"{URL_SUBSCRIPTIONS_BASE}/{subscription['id']}/pause",
        headers=auth_header,
    )
    response = _create_invoice(
        client,
        auth_header,
        type=InvoiceType.SUBSCRIPTION,
        subscription_id=subscription['id'],
    )
    assert response.status_code == status.HTTP_201_CREATED, f"Expected status 201, got {response.status_code}: {response.text}"

def test_list_invoices_no_filter_returns_all_desc_by_created_at(client, auth_header):
    customer_1 = _create_customer(client, auth_header, email="first_customer@subledger.local")
    customer_2 = _create_customer(client, auth_header, email="second_customer@subsledger.local")
    _ = _create_invoice(
        client,
        auth_header,
        customer_id=customer_1['id'],
        description="test invoice from test customer 1"
    )
    _ = _create_invoice(
        client,
        auth_header,
        customer_id=customer_2['id'],
        description="test invoice from test customer 2"
    )
    invoices = client.get(
        f"{URL_INVOICE_BASE}",
        headers=auth_header,
    )
    assert invoices.status_code == status.HTTP_200_OK, f"Expected status 200, got {invoices.status_code}: {invoices.text}"
    assert invoices.json()[0]['created_at'] >= invoices.json()[1]['created_at'], (
        f"Expected invoices in descending order of Invoice.created_at - {invoices.text}"
    )

# (day-5): test_create_subscription_invoice_on_expired_subscription_returns_400
# EXPIRED is system-only (Celery sets it). Test once renewal task exists, or write as a
# service-level test that constructs EXPIRED subscription directly in DB.

# def test_list_invoices_filtered_by_customer_returns_scoped_results(client, auth_header):
#     pass

# def test_list_invoices_filtered_by_status_returns_only_matching(client, auth_header):
#     pass

# def test_create_subscription_invoice_on_expired_subscription(client, auth_header):
#     subscription = _create_subscription(client, auth_header, current_period_end="2026-06-01")




















