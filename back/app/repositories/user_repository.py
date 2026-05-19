from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: str) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    def get_by_oauth(self, provider: str, oauth_id: str) -> User | None:
        return (
            self.db.query(User)
            .filter(User.oauth_provider == provider, User.oauth_id == oauth_id)
            .first()
        )

    def create(self, user: User) -> User:
        self.db.add(user)
        self.db.flush()
        self.db.refresh(user)
        return user

    def delete(self, user: User) -> None:
        self.db.delete(user)

    def save(self, user: User) -> User:
        self.db.flush()
        self.db.refresh(user)
        return user
