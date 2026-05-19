from fastapi import APIRouter, Depends, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.auth import GoogleAuthRequest, TokenResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])
limiter = Limiter(key_func=get_remote_address)


@router.post("/google", response_model=TokenResponse, status_code=200)
@limiter.limit("10/minute")
def google_login(request: Request, body: GoogleAuthRequest, db: Session = Depends(get_db)):
    """Autentica via Google OAuth e retorna JWT. Rate limit: 10 req/min por IP."""
    service = AuthService(db)
    token = service.authenticate_with_google(body.id_token)
    db.commit()
    return TokenResponse(access_token=token)
