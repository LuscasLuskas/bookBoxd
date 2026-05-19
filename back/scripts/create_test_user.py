"""
Cria um usuário de teste no banco e imprime um JWT válido para usar no Swagger.
Uso: docker compose exec backend python scripts/create_test_user.py [--master]
"""
import sys
import uuid
from datetime import datetime, timezone

sys.path.insert(0, ".")

from app.core.database import SessionLocal
from app.core.security import create_access_token
from app.models.user import Role, User

role = Role.MASTER if "--master" in sys.argv else Role.USER

db = SessionLocal()
try:
    user = User(
        id=str(uuid.uuid4()),
        email=f"test-{uuid.uuid4().hex[:6]}@bookboxd.dev",
        name="Test User" if role == Role.USER else "Master User",
        oauth_provider="google",
        oauth_id=f"test-{uuid.uuid4().hex}",
        role=role,
        created_at=datetime.now(timezone.utc),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(user_id=user.id, role=user.role.value, name=user.name)

    print(f"\n✅ Usuário criado:")
    print(f"   ID:    {user.id}")
    print(f"   Email: {user.email}")
    print(f"   Role:  {user.role.value}")
    print(f"\n🔑 JWT (cole no Swagger → Authorize → Bearer <token>):")
    print(f"\n{token}\n")
finally:
    db.close()
