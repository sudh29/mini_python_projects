"""Unit tests for the dashboard_prototype FastAPI backend."""

import pytest

try:
    from app.main import app
    from starlette.testclient import TestClient

    HAS_DASHBOARD_BACKEND = True
except Exception:
    HAS_DASHBOARD_BACKEND = False


@pytest.fixture
def client():
    """Create test client with lifespan context."""
    if not HAS_DASHBOARD_BACKEND:
        pytest.skip("Dashboard backend dependencies not installed")
    with TestClient(app) as test_client:
        yield test_client


def test_dashboard_health_endpoint(client):
    """Verify health check endpoint returns 200 and healthy status."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_dashboard_metrics_endpoint(client):
    """Verify Prometheus metrics are exposed on /metrics."""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert (
        "python_gc_objects_collected_total" in response.text or "http" in response.text
    )


def test_dashboard_docs_endpoint(client):
    """Verify OpenAPI interactive docs are accessible."""
    response = client.get("/docs")
    assert response.status_code == 200


def test_dashboard_login_invalid_credentials(client):
    """Verify 401 Unauthorized when logging in with invalid credentials."""
    response = client.post(
        "/api/auth/login",
        data={"username": "nonexistent_user", "password": "wrong_password"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


def test_dashboard_unauthorized_bots_access(client):
    """Verify protected bot management routes require JWT authentication."""
    response = client.get("/api/bots/status")
    assert response.status_code == 401
