from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import Role, User
from app.repositories.membership_repository import MembershipRepository
from app.repositories.user_repository import UserRepository


def assert_can_view_user(db: Session, viewer: User, target_id: str) -> User:
    """Returns the target user when `viewer` may view their profile, else raises.

    Allowed when: viewer is the target, viewer is MASTER, or both have an
    ACTIVE membership in at least one common club.
    """
    target = UserRepository(db).get_by_id(target_id)
    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado"
        )
    if viewer.id == target.id or viewer.role == Role.MASTER:
        return target
    if MembershipRepository(db).shares_active_club(viewer.id, target.id):
        return target
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Você não compartilha clubes com este usuário",
    )
