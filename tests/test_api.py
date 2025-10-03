"""API endpoint tests."""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
from sqlmodel.pool import StaticPool

from app.main import app
from app.db import get_session
from app.models import User, Song


# Test database setup
@pytest.fixture(name="session")
def session_fixture():
    """Create a test database session."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create a test client."""
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_create_user(client: TestClient):
    """Test user creation endpoint."""
    response = client.post("/api/users", json={"name": "TestUser"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "TestUser"
    assert "id" in data


def test_create_user_idempotent(client: TestClient):
    """Test that creating the same user twice returns the same user."""
    response1 = client.post("/api/users", json={"name": "TestUser"})
    response2 = client.post("/api/users", json={"name": "TestUser"})
    
    assert response1.status_code == 200
    assert response2.status_code == 200
    assert response1.json()["id"] == response2.json()["id"]


def test_health_check(client: TestClient):
    """Test health check endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["app"] == "PlayLister"
