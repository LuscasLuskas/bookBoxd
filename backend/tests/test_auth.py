import pytest
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch


@pytest.fixture
def client():
    return TestClient(app)


def test_get_me_unauthorized(client: TestClient):
    """Test get me endpoint without authentication"""
    response = client.get("/auth/me")
    assert response.status_code == 401


@patch('app.application.services.auth_service.verify_google_token')
def test_login_with_google_new_user(mock_verify, client: TestClient):
    """Test Google login creates new user if not exists"""
    # Mock Google token verification
    mock_verify.return_value = {
        'email': 'testuser@example.com',
        'sub': 'google-123456',
        'name': 'Test User'
    }
    
    response = client.post("/auth/google", json={
        "id_token": "valid_google_token"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert 'access_token' in data
    assert data['token_type'] == 'bearer'


@patch('app.application.services.auth_service.verify_google_token')
def test_login_with_google_existing_user(mock_verify, client: TestClient):
    """Test Google login with existing user"""
    # Mock Google token verification
    mock_verify.return_value = {
        'email': 'testuser@example.com',
        'sub': 'google-123456',
        'name': 'Test User'
    }
    
    # First login to create user
    response1 = client.post("/auth/google", json={
        "id_token": "valid_google_token"
    })
    assert response1.status_code == 200
    token1 = response1.json()['access_token']
    
    # Second login with same user
    response2 = client.post("/auth/google", json={
        "id_token": "valid_google_token"
    })
    assert response2.status_code == 200
    token2 = response2.json()['access_token']
    
    # Both should return valid tokens
    assert token1 is not None
    assert token2 is not None


@patch('app.application.services.auth_service.verify_google_token')
def test_login_with_invalid_google_token(mock_verify, client: TestClient):
    """Test Google login with invalid token"""
    # Mock Google token verification to raise error
    mock_verify.side_effect = Exception("Invalid token")
    
    response = client.post("/auth/google", json={
        "id_token": "invalid_token"
    })
    
    assert response.status_code == 401


@patch('app.application.services.auth_service.verify_google_token')
def test_get_me_with_valid_jwt(mock_verify, client: TestClient):
    """Test get me endpoint with valid JWT token"""
    # Mock Google token verification
    mock_verify.return_value = {
        'email': 'testuser@example.com',
        'sub': 'google-123456',
        'name': 'Test User'
    }
    
    # Login with Google to get JWT token
    login_response = client.post("/auth/google", json={
        "id_token": "valid_google_token"
    })
    
    assert login_response.status_code == 200
    token = login_response.json()['access_token']
    
    # Use token to get user info
    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data['email'] == 'testuser@example.com'
    assert data['name'] == 'Test User'


def test_get_me_with_invalid_jwt(client: TestClient):
    """Test get me endpoint with invalid JWT token"""
    response = client.get(
        "/auth/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    
    assert response.status_code == 401


def test_get_me_missing_auth_header(client: TestClient):
    """Test get me endpoint without auth header"""
    response = client.get("/auth/me")
    
    assert response.status_code == 401