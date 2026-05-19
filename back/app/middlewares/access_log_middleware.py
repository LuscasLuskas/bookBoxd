import uuid
from datetime import datetime, timezone

from jose import JWTError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.database import SessionLocal
from app.core.security import decode_access_token
from app.models.access_log import AccessLog

EXCLUDED_PATHS = {"/health", "/docs", "/openapi.json", "/redoc"}


class AccessLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)

        path = request.url.path
        if any(path.startswith(p) for p in EXCLUDED_PATHS) or path.startswith("/auth"):
            return response

        user_id = self._extract_user_id(request)
        ip_address = self._get_ip(request)

        self._write_log(
            user_id=user_id,
            ip_address=ip_address,
            endpoint=path,
            method=request.method,
            status_code=response.status_code,
        )
        return response

    def _extract_user_id(self, request: Request) -> str | None:
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return None
        token = auth_header[len("Bearer "):]
        try:
            payload = decode_access_token(token)
            return payload.get("sub")
        except JWTError:
            return None

    def _get_ip(self, request: Request) -> str | None:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        if request.client:
            return request.client.host
        return None

    def _write_log(
        self,
        user_id: str | None,
        ip_address: str | None,
        endpoint: str,
        method: str,
        status_code: int,
    ) -> None:
        try:
            db = SessionLocal()
            log = AccessLog(
                id=str(uuid.uuid4()),
                user_id=user_id,
                ip_address=ip_address,
                endpoint=endpoint,
                method=method,
                status_code=status_code,
                created_at=datetime.now(timezone.utc),
            )
            db.add(log)
            db.commit()
        except Exception:
            pass
        finally:
            db.close()
