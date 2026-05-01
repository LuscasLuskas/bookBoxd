from app.infrastructure.auth.google import verify_google_token
from app.infrastructure.auth.jwt import create_access_token
from app.infrastructure.db.repositories.user_repository import UserRepository
from app.infrastructure.db.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession


class AuthService:
    def __init__(self) -> None:
        self.user_repo = UserRepository()

    async def login_with_google(self, session: AsyncSession, id_token: str) -> tuple[User, str]:
        payload = await verify_google_token(id_token)
        email = payload["email"]
        oauth_id = payload["sub"]
        name = payload.get("name")

        user = await self.user_repo.get_by_oauth(session, "google", oauth_id)
        if not user:
            user = await self.user_repo.get_by_email(session, email)

        if not user:
            user = User(
                email=email,
                name=name,
                oauth_provider="google",
                oauth_id=oauth_id,
            )
            await self.user_repo.create(session, user)
        else:
            changed = False
            if user.oauth_provider != "google" or user.oauth_id != oauth_id:
                user.oauth_provider = "google"
                user.oauth_id = oauth_id
                changed = True
            if user.name != name and name is not None:
                user.name = name
                changed = True
            if changed:
                await self.user_repo.create(session, user)

        token = create_access_token(subject=str(user.id), extra_claims={"email": user.email, "role": user.role})
        return user, token
