import uuid
from fastapi import status
from datetime import datetime, timezone, timedelta, date
from app.models.customer import CustomerStatus
from app.models.plan import PlanStatus
from app.models.subscription import Subscription, SubscriptionStatus

URL_SUBSCRIPTIONS_BASE = "/api/v1/subscriptions"
URL_CUSTOMERS_BASE = "/api/v1/customers"
URL_PLANS_BASE = "/api/v1/plans"

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

def _create_subscription(client, auth_header, test_failure: bool = False, **overrides):
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
    if test_failure:
        assert response.status_code == status.HTTP_400_BAD_REQUEST, f"Expected 400 for _create_subscription, got {response.status_code}: {response.text}"
    else:
        assert response.status_code == status.HTTP_201_CREATED, f"Expected 201 for _create_subscription, got {response.status_code}: {response.text}"
    return response.json()

# Auth + happy-path tests:

# test_create_subscription_unauthorized — no auth header → 401
def test_create_subscription_unauthorized(client, auth_header):
    customer = _create_customer(client, auth_header)
    plan = _create_plan(client, auth_header)

    response = client.post(
        URL_SUBSCRIPTIONS_BASE,
        json={
            "customer_id": customer["id"],
            "plan_id": plan["id"],
            "start_date": "2026-06-27",
            "current_period_start": "2026-06-27",
            "current_period_end": "2036-06-27"
        },
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED, f"Expected 401, got {response.status_code}: {response.text}"

# test_create_subscription — valid plan + customer → 201, status="active"
def test_create_subscription(client, auth_header):
    customer = _create_customer(client, auth_header)
    plan = _create_plan(client, auth_header)
    body = _create_subscription(
        client,
        auth_header,
        customer_id=customer["id"],
        plan_id=plan["id"]
    )
    # Round-trip: what we sent comes back unchanged
    assert body["customer_id"] == customer["id"], f"customer_id mismatch: {body}"
    assert body["plan_id"] == plan["id"], f"plan_id mismatch: {body}"
    assert body["start_date"] == "2026-06-27", f"start_date mismatch: {body}"
    assert body["current_period_start"] == "2026-06-27", f"current_period_start mismatch: {body}"
    assert body["current_period_end"] == "2036-06-27", f"current_period_end mismatch: {body}"
    
    # Server-controlled fields: status hardcoded ACTIVE, lifecycle stamps null
    assert body["status"] == SubscriptionStatus.ACTIVE.value, f"Expected status=active, got {body['status']}"
    assert body["paused_at"] is None, f"paused_at should be null on create: {body}"
    assert body["resumed_at"] is None, f"resumed_at should be null on create: {body}"
    assert body["cancelled_at"] is None, f"cancelled_at should be null on create: {body}"
    assert body["expired_at"] is None, f"expired_at should be null on create: {body}"
    
    # Server-populated fields
    assert body["id"], f"id missing: {body}"
    uuid.UUID(body["id"])  # validates it's a real UUID, not just truthy
    assert body["created_at"], f"created_at missing: {body}"

# test_get_subscriptions — create one, GET → 200, len >= 1
def test_get_subscriptions(client, auth_header):
    _ = _create_subscription(client, auth_header)
    response = client.get(
        f"{URL_SUBSCRIPTIONS_BASE}",
        headers=auth_header,
    )
    assert response.status_code == status.HTTP_200_OK, f"Expected 200, got {response.status_code}: {response.text}"
    assert len(response.json()) >= 1, f"Failed to fetch subscription, {response.text}"

# test_get_subscription_by_id — create, GET by id → 200, ids match
def test_get_subscription_by_id(client, auth_header):
    subscription = _create_subscription(client, auth_header)
    response = client.get(
        f"{URL_SUBSCRIPTIONS_BASE}/{subscription['id']}",
        headers=auth_header,
    )
    assert response.status_code == status.HTTP_200_OK, f"Failed to fetch subscription with id: {subscription['id']} - {response.text}"
    assert response.json()["id"] == subscription["id"], f"ID match failure - response_id: {response.json()['id']} - request_id: {subscription['id']}"

# State machine validation tests (this is the part PulseNotify lacked):

# 5. test_pause_active_subscription → 200, status="paused", paused_at set
def test_pause_active_subscription(client, auth_header):
    subscription = _create_subscription(client, auth_header)
    response = client.patch(
        f"{URL_SUBSCRIPTIONS_BASE}/{subscription['id']}/pause",
        headers=auth_header,
    )
    assert response.status_code == status.HTTP_200_OK, f"Expected 200, got {response.status_code}: {response.text}"
    assert response.json()["status"] == SubscriptionStatus.PAUSED.value, f"Expected status: {SubscriptionStatus.PAUSED.value}, recieved {response.json()['status']} - {response.text}"
    assert response.json()["paused_at"] is not None, f"Expected a datetime for subscription.paused_at, recieved {response.json()['paused_at']} - {response.text}"

# 6. test_pause_already_paused_fails → create, pause once (200), pause again → 400
def test_pause_already_paused_fails(client, auth_header):
    subscription = _create_subscription(client, auth_header)
    response = client.patch(
        f"{URL_SUBSCRIPTIONS_BASE}/{subscription['id']}/pause",
        headers=auth_header,
    )
    assert response.status_code == status.HTTP_200_OK, f"Expected 200, got {response.status_code}: {response.text}"
    response_2 = client.patch(
        f"{URL_SUBSCRIPTIONS_BASE}/{subscription['id']}/pause",
        headers=auth_header,
    )
    assert response_2.status_code == status.HTTP_400_BAD_REQUEST, f"Expected 400, got {response_2.status_code}: {response_2.text}"

# 7. test_resume_paused_subscription → create, pause, resume → 200, status="active", current_period_end extended
def test_resume_paused_subscription(client, auth_header, db_session):
    subscription = _create_subscription(client, auth_header)
    pause_response = client.patch(
        f"{URL_SUBSCRIPTIONS_BASE}/{subscription['id']}/pause",
        headers=auth_header,
    )
    assert pause_response.status_code == status.HTTP_200_OK, f"Expected 200, got {pause_response.status_code}: {pause_response.text}"
    assert pause_response.json()["status"] == SubscriptionStatus.PAUSED.value, f"Expected status: {SubscriptionStatus.PAUSED.value}, recieved {pause_response.json()['status']} - {pause_response.text}"

    original_period_end = subscription["current_period_end"]

    # Backdate paused_at by 5 days to simulate a multi-day pause
    sub_in_db = db_session.get(Subscription, uuid.UUID(subscription["id"]))
    sub_in_db.paused_at = datetime.now(timezone.utc) - timedelta(days=5)
    db_session.flush()

    resume_response = client.patch(
        f"{URL_SUBSCRIPTIONS_BASE}/{subscription['id']}/resume",
        headers=auth_header,
    )
    assert resume_response.status_code == status.HTTP_200_OK, f"Expected 200, got {resume_response.status_code}: {resume_response.text}"
    assert resume_response.json()["status"] == SubscriptionStatus.ACTIVE.value, f"Expected status: {SubscriptionStatus.ACTIVE.value}, recieved {resume_response.json()['status']} - {resume_response.text}"
    assert resume_response.json()["resumed_at"] is not None, f"Expected a datetime for subscription.resumed_at, recieved {resume_response.json()['resumed_at']} - {resume_response.text}"

    new_period_end = date.fromisoformat(resume_response.json()["current_period_end"])
    expected_period_end = date.fromisoformat(original_period_end) + timedelta(days=5)
    assert new_period_end == expected_period_end, f"Unexpected time difference pause -> resume  - {resume_response.text}"

# 8. test_resume_active_fails → create, resume without pausing → 400
def test_resume_active_fails(client, auth_header):
    subscription = _create_subscription(client, auth_header)
    response = client.patch(
        f"{URL_SUBSCRIPTIONS_BASE}/{subscription['id']}/resume",
        headers=auth_header,
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST, f"Expected 400, got {response.status_code}: {response.text}"

# 9. test_cancel_active_subscription → 200, status="cancelled"
def test_cancel_active_subscription(client, auth_header):
    subscription = _create_subscription(client, auth_header)
    response = client.patch(
        f"{URL_SUBSCRIPTIONS_BASE}/{subscription['id']}/cancel",
        headers=auth_header,
    )
    assert response.status_code == status.HTTP_200_OK, f"Expected 200, got {response.status_code}: {response.text}"
    assert response.json()["status"] == SubscriptionStatus.CANCELLED.value, f"Expected status: {SubscriptionStatus.CANCELLED.value}, recieved {response.json()['status']} - {response.text}"
    assert response.json()["cancelled_at"] is not None, f"Expected a datetime for subscription.cancelled_at, recieved {response.json()['cancelled_at']} - {response.text}"

# 10. test_cancel_already_cancelled_fails → cancel twice → 400
def test_cancel_already_cancelled_fails(client, auth_header):
    subscription = _create_subscription(client, auth_header)
    cancel_response = client.patch(
        f"{URL_SUBSCRIPTIONS_BASE}/{subscription['id']}/cancel",
        headers=auth_header,
    )
    assert cancel_response.status_code == status.HTTP_200_OK, f"Expected 200, got {cancel_response.status_code}: {cancel_response.text}"
    assert cancel_response.json()["status"] == SubscriptionStatus.CANCELLED.value, f"Expected status: {SubscriptionStatus.CANCELLED.value}, recieved {cancel_response.json()['status']} - {cancel_response.text}"
    cancel_response_2 = client.patch(
        f"{URL_SUBSCRIPTIONS_BASE}/{subscription['id']}/cancel",
        headers=auth_header,
    )
    assert cancel_response_2.status_code == status.HTTP_400_BAD_REQUEST, f"Expected 400, got {cancel_response_2.status_code}: {cancel_response_2.text}"

# 11. test_cancel_paused_subscription → create, pause, cancel → 200 (cancel from paused is legal)
def test_cancel_paused_subscription(client, auth_header):
    subscription = _create_subscription(client, auth_header)
    pause_response = client.patch(
        f"{URL_SUBSCRIPTIONS_BASE}/{subscription['id']}/pause",
        headers=auth_header,
    )
    assert pause_response.status_code == status.HTTP_200_OK, f"Expected 200, got {pause_response.status_code}: {pause_response.text}"
    assert pause_response.json()["status"] == SubscriptionStatus.PAUSED.value, f"Expected status: {SubscriptionStatus.PAUSED.value}, recieved {pause_response.json()['status']} - {pause_response.text}"
    cancel_response = client.patch(
        f"{URL_SUBSCRIPTIONS_BASE}/{subscription['id']}/cancel",
        headers=auth_header,
    )
    assert cancel_response.status_code == status.HTTP_200_OK, f"Expected 200, got {cancel_response.status_code}: {cancel_response.text}"
    assert cancel_response.json()["status"] == SubscriptionStatus.CANCELLED.value, f"Expected status: {SubscriptionStatus.CANCELLED.value}, recieved {cancel_response.json()['status']} - {cancel_response.text}"

# Business validation tests:

# 12. test_create_with_inactive_customer_fails → create customer, PATCH to inactive, try subscription → 400
def test_create_with_inactive_customer_fails(client, auth_header):
    customer = _create_customer(client, auth_header)
    _ = client.patch(
        f"{URL_CUSTOMERS_BASE}/{customer['id']}",
        json={
            "status": "inactive",
        },
        headers=auth_header,
    )
    _ = _create_subscription(
        client,
        auth_header,
        test_failure=True,
        customer_id=customer['id'],
    )

# 13. test_create_with_inactive_plan_fails → same shape with plan
def test_create_with_inactive_plan_fails(client, auth_header):
    plan = _create_plan(client, auth_header)
    _ = client.patch(
        f"{URL_PLANS_BASE}/{plan['id']}",
        json={
            "status": "inactive",
        },
        headers=auth_header,
    )
    _ = _create_subscription(
        client,
        auth_header,
        test_failure=True,
        plan_id=plan['id'],
    )

# 14. test_create_duplicate_active_fails → create, try same customer+plan again → 409
def test_create_duplicate_active_fails(client, auth_header):
    response_1 = _create_subscription(client, auth_header)
    response_2 = client.post(
        URL_SUBSCRIPTIONS_BASE,
        json={
            "customer_id": response_1["customer_id"],
            "plan_id": response_1["plan_id"],
            "start_date": "2026-06-27",
            "current_period_start": "2026-06-27",
            "current_period_end": "2036-06-27"
        },
        headers=auth_header,
    )
    assert response_2.status_code == status.HTTP_409_CONFLICT, f"Expected 409 for test_create_duplicate_active_fails, got {response_2.status_code}: {response_2.text}"
    

# Query filtering test:

# 15. test_filter_by_status → create A (active), create B + cancel, GET ?status=active → 1 result
def test_filter_by_status(client, auth_header):
    subscription_A = _create_subscription(client, auth_header)
    customer_B = _create_customer(
        client,
        auth_header,
        email="new-test-customer@subledger.local",
    )
    plan_B = _create_plan(
        client,
        auth_header,
        name="new-test-plan",
    )
    subscription_B = _create_subscription(
        client,
        auth_header,
        customer_id=customer_B['id'],
        plan_id=plan_B['id'],
    )
    cancelled_subscription_B = client.patch(
        f"{URL_SUBSCRIPTIONS_BASE}/{subscription_B['id']}/cancel",
        headers=auth_header,
    )
    assert cancelled_subscription_B.status_code == status.HTTP_200_OK, f"Expected 200, got {cancelled_subscription_B.status_code}: {cancelled_subscription_B.text}"
    assert cancelled_subscription_B.json()["status"] == SubscriptionStatus.CANCELLED.value, f"Expected status: {SubscriptionStatus.CANCELLED.value}, recieved {cancelled_subscription_B.json()['status']} - {cancelled_subscription_B.text}"

    response = client.get(
        f"{URL_SUBSCRIPTIONS_BASE}?status=active",
        headers=auth_header,
    )
    assert response.status_code == status.HTTP_200_OK, f"Expected 200, got {response.status_code}: {response.text}"
    assert len(response.json()) == 1, f"Failure fetching, {response.text}"

