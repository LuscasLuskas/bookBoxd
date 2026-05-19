"""Tests for User CRUD and deletion (T05)."""
import uuid

from tests.conftest import make_user
from app.models.user import Role


def test_get_me(client, db):
    user, token = make_user(db)
    response = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == user.email
    assert data["id"] == user.id


def test_get_me_no_token(client):
    response = client.get("/users/me")
    assert response.status_code == 401


def test_delete_me(client, db):
    user, token = make_user(db)
    response = client.delete("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200

    from app.models.user import User
    remaining = db.query(User).filter(User.id == user.id).first()
    assert remaining is None


def test_delete_me_transfers_club_ownership(client, db):
    from app.models.book_club import BookClub
    from app.models.membership import Membership, MembershipStatus

    owner, token = make_user(db, name="Owner")
    member, _ = make_user(db, name="Member")

    club = BookClub(id=str(uuid.uuid4()), name="Club", owner_id=owner.id)
    db.add(club)
    db.flush()

    db.add(Membership(
        id=str(uuid.uuid4()), user_id=owner.id, club_id=club.id, status=MembershipStatus.ACTIVE
    ))
    db.add(Membership(
        id=str(uuid.uuid4()), user_id=member.id, club_id=club.id, status=MembershipStatus.ACTIVE
    ))
    db.commit()

    response = client.delete("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200

    db.refresh(club)
    assert club.owner_id == member.id


def test_master_can_delete_other_user(client, db):
    master, master_token = make_user(db, role=Role.MASTER, name="Master")
    target, _ = make_user(db, name="Target")

    response = client.delete(
        f"/users/{target.id}", headers={"Authorization": f"Bearer {master_token}"}
    )
    assert response.status_code == 200

    from app.models.user import User
    remaining = db.query(User).filter(User.id == target.id).first()
    assert remaining is None


def test_non_master_cannot_delete_other_user(client, db):
    user1, token1 = make_user(db, name="User1")
    user2, _ = make_user(db, name="User2")

    response = client.delete(
        f"/users/{user2.id}", headers={"Authorization": f"Bearer {token1}"}
    )
    assert response.status_code == 403
