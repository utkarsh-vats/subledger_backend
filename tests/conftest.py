import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from app.core.config import settings
from app.db.base import Base
from app.api.deps import get_db
from app.main import app
from app.core.security import hash_password

@pytest.fixture(scope="session")
def engine():
    engine = create_engine(settings.test_database_url)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()

@pytest.fixture(scope="session", autouse=True)
def override_admin_credentials():
    test_password = "test-admin-password"
    original_hash = settings.ADMIN_PASSWORD_HASH
    settings.ADMIN_PASSWORD_HASH = hash_password(test_password)
    yield test_password
    settings.ADMIN_PASSWORD_HASH = original_hash

@pytest.fixture(scope="function")
def db_session(engine):
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    # Your services call session.commit(). We swap commit for flush so
    # data becomes visible to subsequent queries WITHIN the test, but the
    # outer transaction never finalizes — rollback at end wipes everything.
    session.commit = session.flush

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def admin_token(client, override_admin_credentials):
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": settings.ADMIN_EMAIL,
            "password": override_admin_credentials,
        },
    )
    assert response.status_code == 200, f"Login failed: {response.text}"
    return response.json()["access_token"]

@pytest.fixture(scope="function")
def auth_header(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}





