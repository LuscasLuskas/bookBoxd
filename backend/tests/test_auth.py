import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_get_me_unauthorized(client: TestClient):
    """Test get me endpoint without authentication"""
    response = client.get("/auth/me")
    assert response.status_code == 401