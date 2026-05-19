"""Tests covering ALL valid and invalid Membership transitions (T08)."""
import uuid
from datetime import datetime, timedelta, timezone

import pytest

from app.models.membership import Membership, MembershipStatus
from app.models.user import Role
from app.services.membership_service import MembershipService
from tests.conftest import make_user


def make_club(db, owner):
    from app.models.book_club import BookClub
    from app.models.membership import Membership, MembershipStatus

    club = BookClub(
        id=str(uuid.uuid4()),
        name="Test Club",
        owner_id=owner.id,
    )
    db.add(club)
    db.flush()

    membership = Membership(
        id=str(uuid.uuid4()),
        user_id=owner.id,
        club_id=club.id,
        status=MembershipStatus.ACTIVE,
    )
    db.add(membership)
    db.commit()
    db.refresh(club)
    return club


def test_join_creates_pending(db):
    owner, _ = make_user(db, name="Owner")
    member, _ = make_user(db, name="Member")
    club = make_club(db, owner)

    service = MembershipService(db)
    m = service.join(club.id, member)
    db.commit()

    assert m.status == MembershipStatus.PENDING
    assert m.user_id == member.id


def test_join_banned_raises_403(db):
    from fastapi import HTTPException

    owner, _ = make_user(db, name="Owner")
    member, _ = make_user(db, name="Member")
    club = make_club(db, owner)

    m = Membership(
        id=str(uuid.uuid4()),
        user_id=member.id,
        club_id=club.id,
        status=MembershipStatus.BANNED,
    )
    db.add(m)
    db.commit()

    service = MembershipService(db)
    with pytest.raises(HTTPException) as exc:
        service.join(club.id, member)
    assert exc.value.status_code == 403


def test_join_active_raises_409(db):
    from fastapi import HTTPException

    owner, _ = make_user(db, name="Owner")
    member, _ = make_user(db, name="Member")
    club = make_club(db, owner)

    m = Membership(
        id=str(uuid.uuid4()),
        user_id=member.id,
        club_id=club.id,
        status=MembershipStatus.ACTIVE,
    )
    db.add(m)
    db.commit()

    service = MembershipService(db)
    with pytest.raises(HTTPException) as exc:
        service.join(club.id, member)
    assert exc.value.status_code == 409


def test_approve_pending_to_active(db):
    owner, _ = make_user(db, name="Owner")
    member, _ = make_user(db, name="Member")
    club = make_club(db, owner)

    service = MembershipService(db)
    service.join(club.id, member)
    db.commit()

    m = service.approve(club.id, member.id, owner)
    db.commit()

    assert m.status == MembershipStatus.ACTIVE


def test_reject_pending(db):
    owner, _ = make_user(db, name="Owner")
    member, _ = make_user(db, name="Member")
    club = make_club(db, owner)

    service = MembershipService(db)
    service.join(club.id, member)
    db.commit()

    m = service.reject(club.id, member.id, owner)
    db.commit()

    assert m.status == MembershipStatus.REJECTED


def test_leave_active_to_left(db):
    owner, _ = make_user(db, name="Owner")
    member, _ = make_user(db, name="Member")
    club = make_club(db, owner)

    service = MembershipService(db)
    service.join(club.id, member)
    db.commit()
    service.approve(club.id, member.id, owner)
    db.commit()

    m = service.leave(club.id, member)
    db.commit()
    assert m.status == MembershipStatus.LEFT


def test_ban_blocks_reentry(db):
    from fastapi import HTTPException

    owner, _ = make_user(db, name="Owner")
    member, _ = make_user(db, name="Member")
    club = make_club(db, owner)

    service = MembershipService(db)
    service.join(club.id, member)
    db.commit()
    service.approve(club.id, member.id, owner)
    db.commit()
    service.ban(club.id, member.id, owner)
    db.commit()

    with pytest.raises(HTTPException) as exc:
        service.join(club.id, member)
    assert exc.value.status_code == 403


def test_left_allows_rejoin(db):
    owner, _ = make_user(db, name="Owner")
    member, _ = make_user(db, name="Member")
    club = make_club(db, owner)

    service = MembershipService(db)
    service.join(club.id, member)
    db.commit()
    service.approve(club.id, member.id, owner)
    db.commit()
    service.leave(club.id, member)
    db.commit()

    m = service.join(club.id, member)
    db.commit()
    assert m.status == MembershipStatus.PENDING


def test_kick_blocks_before_expiry(db):
    from fastapi import HTTPException

    owner, _ = make_user(db, name="Owner")
    member, _ = make_user(db, name="Member")
    club = make_club(db, owner)

    future = datetime.now(timezone.utc) + timedelta(days=7)

    service = MembershipService(db)
    service.join(club.id, member)
    db.commit()
    service.approve(club.id, member.id, owner)
    db.commit()
    service.kick(club.id, member.id, future, owner)
    db.commit()

    with pytest.raises(HTTPException) as exc:
        service.join(club.id, member)
    assert exc.value.status_code == 403


def test_kick_allows_rejoin_after_expiry(db):
    owner, _ = make_user(db, name="Owner")
    member, _ = make_user(db, name="Member")
    club = make_club(db, owner)

    past = datetime.now(timezone.utc) - timedelta(days=1)

    service = MembershipService(db)
    service.join(club.id, member)
    db.commit()
    service.approve(club.id, member.id, owner)
    db.commit()
    service.kick(club.id, member.id, datetime.now(timezone.utc) + timedelta(days=1), owner)
    db.commit()

    m_repo = db.query(Membership).filter(
        Membership.user_id == member.id, Membership.club_id == club.id
    ).first()
    m_repo.kicked_until = past
    db.commit()

    m = service.join(club.id, member)
    db.commit()
    assert m.status == MembershipStatus.PENDING


def test_non_owner_cannot_approve(db):
    from fastapi import HTTPException

    owner, _ = make_user(db, name="Owner")
    member, _ = make_user(db, name="Member")
    outsider, _ = make_user(db, name="Outsider")
    club = make_club(db, owner)

    service = MembershipService(db)
    service.join(club.id, member)
    db.commit()

    with pytest.raises(HTTPException) as exc:
        service.approve(club.id, member.id, outsider)
    assert exc.value.status_code == 403


def test_owner_cannot_leave(db):
    from fastapi import HTTPException

    owner, _ = make_user(db, name="Owner")
    club = make_club(db, owner)

    service = MembershipService(db)
    with pytest.raises(HTTPException) as exc:
        service.leave(club.id, owner)
    assert exc.value.status_code == 400
