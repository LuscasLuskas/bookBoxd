import uuid

import requests
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token
from app.models.user import Role, User
from app.repositories.user_repository import UserRepository


GOOGLE_TOKENINFO_URL = "https://oauth2.googleapis.com/tokeninfo"
GOOGLE_VALID_ISSUERS = {"accounts.google.com", "https://accounts.google.com"}


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    def authenticate_with_google(self, id_token: str) -> str:
        google_data = self._verify_google_token(id_token)
        user = self._get_or_create_user(google_data)
        return create_access_token(
            user_id=user.id,
            role=user.role.value,
            name=user.name,
        )

    def _verify_google_token(self, id_token: str) -> dict:
        response = requests.get(GOOGLE_TOKENINFO_URL, params={"id_token": id_token}, timeout=10)
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token do Google inválido",
            )
        data = response.json()
        if data.get("aud") != settings.GOOGLE_CLIENT_ID:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token não pertence a este aplicativo",
            )
        if data.get("iss") not in GOOGLE_VALID_ISSUERS:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Emissor do token não é o Google",
            )
        # tokeninfo returns "email_verified" as the string "true"/"false".
        if str(data.get("email_verified")).lower() != "true":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email do Google não verificado",
            )
        return data

    def _get_or_create_user(self, google_data: dict) -> User:
        oauth_id = google_data.get("sub")
        email = google_data.get("email")
        name = google_data.get("name", email)

        user = self.user_repo.get_by_oauth(provider="google", oauth_id=oauth_id)
        if user:
            return user

        existing_by_email = self.user_repo.get_by_email(email)
        if existing_by_email:
            existing_by_email.oauth_id = oauth_id
            existing_by_email.oauth_provider = "google"
            return self.user_repo.save(existing_by_email)

        new_user = User(
            id=str(uuid.uuid4()),
            email=email,
            name=name,
            oauth_provider="google",
            oauth_id=oauth_id,
            role=Role.USER,
        )
        return self.user_repo.create(new_user)
