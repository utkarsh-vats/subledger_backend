from fastapi import status
from decimal import Decimal
from app.models.plan import PlanStatus

def test_create_plan_unauthorized(client):
    plan_response = client.post(
        "/api/v1/plans",
        json={
            "name": "unauthorized-plan",
            "description": "test_create_plan_unauthorized",
            "billing_cycle": "monthly",
            "price": 100.0,
            "currency": "INR",
            "status": "active"
        }
    )
    assert plan_response.status_code == status.HTTP_401_UNAUTHORIZED, f"Expected 401, got {plan_response.status_code}: {plan_response.text}"

def test_create_plan(client, auth_header):
    plan_response = client.post(
        "/api/v1/plans",
        json={
            "name": "authorized-plan",
            "description": "test_create_plan",
            "billing_cycle": "monthly",
            "price": 100.0,
            "currency": "INR",
            "status": "active"
        },
        headers=auth_header,
    )
    assert plan_response.status_code == status.HTTP_201_CREATED, f"Expected 201, got {plan_response.status_code}: {plan_response.text}"
    assert plan_response.json()["id"], f"Failed to create plan.id - {plan_response.text}"
    assert plan_response.json()["name"] == "authorized-plan", f"Failed to create plan.name - {plan_response.text}"
    assert plan_response.json()["description"] == "test_create_plan", f"Failed to create plan.description - {plan_response.text}"
    assert plan_response.json()["billing_cycle"], f"Failed to create plan.billing_cycle - {plan_response.text}"
    assert Decimal(plan_response.json()["price"]) > 0.0, f"Expected a positive value for plan.price - {plan_response.text}"
    assert len(plan_response.json()["currency"]) == 3, f"Expected a standard ISO 4217 value - {plan_response.json()['currency']}"
    assert plan_response.json()["status"] == PlanStatus.ACTIVE.value, f"Expected plan.status = 'active' - {plan_response.json()['status']} - {plan_response.text}"
    assert plan_response.json()["created_at"], f"Failed to create plan.created_at - {plan_response.text}"
    assert plan_response.json()["updated_at"], f"Failed to create plan.updated_at - {plan_response.text}"

def test_get_plans(client, auth_header):
    _ = client.post(
        "/api/v1/plans",
        json={
            "name": "test-plan",
            "description": "test_get_plans",
            "billing_cycle": "monthly",
            "price": 100.0,
            "currency": "INR",
            "status": "active"
        },
        headers=auth_header,
    )
    plan_responses = client.get(
        "/api/v1/plans",
        headers=auth_header,
    )
    assert plan_responses.status_code == status.HTTP_200_OK, f"Expected 200, got {plan_responses.status_code}: {plan_responses.text}"
    assert len(plan_responses.json()) >= 1, f"Failed to fetch created plan - {plan_responses.json()}"

def test_get_plan_by_id(client, auth_header):
    test_plan = client.post(
        "/api/v1/plans",
        json={
            "name": "test-plan",
            "description": "test_get_plan_by_id",
            "billing_cycle": "monthly",
            "price": 100.0,
            "currency": "INR",
            "status": "active"
        },
        headers=auth_header,
    )
    plan_response = client.get(
        f"/api/v1/plans/{test_plan.json()['id']}",
        headers=auth_header,
    )
    assert plan_response.status_code == status.HTTP_200_OK, f"Expected 200, got {plan_response.status_code}: {plan_response.text}"
    assert plan_response.json()["id"] == test_plan.json()["id"], f"ID match failure - plan response: {plan_response.json()['id']} - test plan: {test_plan.json()['id']}"

def test_update_plan(client, auth_header):
    test_plan = client.post(
        "/api/v1/plans",
        json={
            "name": "test-plan",
            "description": "test_get_plan_by_id",
            "billing_cycle": "monthly",
            "price": 100.0,
            "currency": "INR",
            "status": "active"
        },
        headers=auth_header,
    )
    plan_response = client.patch(
        f"/api/v1/plans/{test_plan.json()['id']}",
        json={
            "status": "inactive",
        },
        headers=auth_header,
    )
    assert plan_response.status_code == status.HTTP_200_OK, f"Expected 200, got {plan_response.status_code}: {plan_response.text}"
    assert plan_response.json()["status"] == PlanStatus.INACTIVE.value, f"Expected plan.status = 'inactive', got {plan_response.json()['status']}: {plan_response.text}"
    
