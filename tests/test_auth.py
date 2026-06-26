from app.core.config import settings
from fastapi import status

# test_login_success
def test_login_success(client, override_admin_credentials):
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": settings.ADMIN_EMAIL,
            "password": override_admin_credentials,
        }
    )
    assert response.status_code == status.HTTP_200_OK, f"Login failed - {response.text}"
    assert response.json()["access_token"], f"Test failed - {response.text}"

# test_login_wrong_password
def test_login_wrong_password(client):
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": settings.ADMIN_EMAIL,
            "password": "random-string-as-wrong-password",
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED, f"Expected 401, got {response.status_code}: {response.text}"
