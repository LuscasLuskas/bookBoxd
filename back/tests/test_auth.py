from unittest.mock import patch

import pytest

from app.core.config import settings
from app.services.auth_service import AuthService


GOOGLE_USER_DATA = {
    "sub": "google-sub-123",
    "email": "test@example.com",
    "name": "Test User",
    "aud": settings.GOOGLE_CLIENT_ID or "test-client-id",
}


@patch("app.services.auth_service.requests.get")
def test_authenticate_creates_new_user(mock_get, db):
    settings.GOOGLE_CLIENT_ID = "test-client-id"
    mock_response = mock_get.return_value
    mock_response.status_code = 200
    mock_response.json.return_value = {**GOOGLE_USER_DATA, "aud": "test-client-id"}

    service = AuthService(db)
    token = service.authenticate_with_google("fake-id-token")
    db.commit()

    assert token is not None
    assert len(token) > 0

    from app.repositories.user_repository import UserRepository
    repo = UserRepository(db)
    user = repo.get_by_oauth("google", "google-sub-123")
    assert user is not None
    assert user.email == "test@example.com"


@patch("app.services.auth_service.requests.get")
def test_authenticate_returns_existing_user(mock_get, db):
    settings.GOOGLE_CLIENT_ID = "test-client-id"
    mock_response = mock_get.return_value
    mock_response.status_code = 200
    mock_response.json.return_value = {**GOOGLE_USER_DATA, "aud": "test-client-id"}

    service = AuthService(db)
    token1 = service.authenticate_with_google("fake-id-token")
    db.commit()
    token2 = service.authenticate_with_google("fake-id-token")
    db.commit()

    from app.repositories.user_repository import UserRepository
    repo = UserRepository(db)
    from app.models.user import User
    count = db.query(User).filter(User.oauth_id == "google-sub-123").count()
    assert count == 1


@patch("app.services.auth_service.requests.get")
def test_authenticate_invalid_token(mock_get, db):
    mock_response = mock_get.return_value
    mock_response.status_code = 400
    mock_response.json.return_value = {"error": "invalid_token"}

    from fastapi import HTTPException
    service = AuthService(db)
    with pytest.raises(HTTPException) as exc_info:
        service.authenticate_with_google("invalid-token")
    assert exc_info.value.status_code == 401


@patch("app.services.auth_service.requests.get")
def test_authenticate_wrong_audience(mock_get, db):
    settings.GOOGLE_CLIENT_ID = "correct-client-id"
    mock_response = mock_get.return_value
    mock_response.status_code = 200
    mock_response.json.return_value = {**GOOGLE_USER_DATA, "aud": "wrong-client-id"}

    from fastapi import HTTPException
    service = AuthService(db)
    with pytest.raises(HTTPException) as exc_info:
        service.authenticate_with_google("fake-token")
    assert exc_info.value.status_code == 401
