from fastapi import status
from app.models.customer import CustomerStatus

URL_CUSTOMERS_BASE = "/api/v1/customers"

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

def test_create_customer_unauthorized(client):
    response = client.post(
        URL_CUSTOMERS_BASE,
        json={
            "name": "test-customer-unauthorized",
            "email": "testcustomer@subledger.local",
            "company_name": "subledget_local",
            "status": "active",
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED, f"Expected 401, got {response.status_code}: {response.text}"

def test_create_customer(client, auth_header):
    response = _create_customer(client, auth_header)
    assert response["id"], f"Failed to create customer.id - {response}"
    assert response["name"], f"Failed to create customer.name - {response}"
    assert response["email"], f"Failed to create customer.email - {response}"
    assert response["company_name"], f"Failed to create customer.company_name - {response}"
    assert response["status"] == CustomerStatus.ACTIVE.value, f"Expected customer.status = 'active' - {response['status']} - {response}"
    assert response["created_at"], f"Failed to create customer.created_at - {response}"
    assert response["updated_at"], f"Failed to create customer.updated_at - {response}"

def test_get_customers(client, auth_header):
    _ = _create_customer(client, auth_header)
    customer_responses = client.get(
        URL_CUSTOMERS_BASE,
        headers=auth_header,
    )
    assert customer_responses.status_code == status.HTTP_200_OK, f"Expected 200, got {customer_responses.status_code}: {customer_responses.text}"
    assert len(customer_responses.json()) >= 1, f"Failed to fetch created customer - {customer_responses.json()}"

def test_get_customer_by_id(client, auth_header):
    response = _create_customer(client, auth_header)
    customer_response = client.get(
        f"{URL_CUSTOMERS_BASE}/{response['id']}",
        headers=auth_header,
    )
    assert customer_response.status_code == status.HTTP_200_OK, f"Expected 200, got {customer_response.status_code}: {customer_response.text}"
    assert customer_response.json()["id"] == response["id"], f"ID match failure - customer response: {customer_response.json()['id']} - test customer: {response['id']}"

def test_update_customer(client, auth_header):
    response = _create_customer(client, auth_header)
    customer_response = client.patch(
        f"{URL_CUSTOMERS_BASE}/{response['id']}",
        json={
            "status": "inactive",
        },
        headers=auth_header,
    )
    assert customer_response.status_code == status.HTTP_200_OK, f"Expected 200, got {customer_response.status_code}: {customer_response.text}"
    assert customer_response.json()["status"] == CustomerStatus.INACTIVE.value, f"Expected customer.status = 'inactive', got {customer_response.json()['status']}: {customer_response.text}"
    
