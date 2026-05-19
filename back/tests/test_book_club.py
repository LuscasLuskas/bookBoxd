"""Tests for BookClub CRUD (T07)."""
from app.models.user import Role
from tests.conftest import make_user


def test_create_club(client, db):
    user, token = make_user(db)
    response = client.post(
        "/clubs",
        json={"name": "Clube dos Leitores", "description": "Um clube bacana"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Clube dos Leitores"
    assert data["owner_id"] == user.id


def test_get_club(client, db):
    user, token = make_user(db)
    create_resp = client.post(
        "/clubs", json={"name": "Club X"}, headers={"Authorization": f"Bearer {token}"}
    )
    club_id = create_resp.json()["id"]

    response = client.get(f"/clubs/{club_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["id"] == club_id


def test_update_club_owner(client, db):
    user, token = make_user(db)
    create_resp = client.post(
        "/clubs", json={"name": "Old Name"}, headers={"Authorization": f"Bearer {token}"}
    )
    club_id = create_resp.json()["id"]

    response = client.patch(
        f"/clubs/{club_id}",
        json={"name": "New Name"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "New Name"


def test_update_club_non_owner_forbidden(client, db):
    owner, owner_token = make_user(db, name="Owner")
    other, other_token = make_user(db, name="Other")

    create_resp = client.post(
        "/clubs", json={"name": "Club"}, headers={"Authorization": f"Bearer {owner_token}"}
    )
    club_id = create_resp.json()["id"]

    response = client.patch(
        f"/clubs/{club_id}",
        json={"name": "Hacked"},
        headers={"Authorization": f"Bearer {other_token}"},
    )
    assert response.status_code == 403


def test_master_can_update_any_club(client, db):
    owner, owner_token = make_user(db, name="Owner")
    master, master_token = make_user(db, role=Role.MASTER, name="Master")

    create_resp = client.post(
        "/clubs", json={"name": "Club"}, headers={"Authorization": f"Bearer {owner_token}"}
    )
    club_id = create_resp.json()["id"]

    response = client.patch(
        f"/clubs/{club_id}",
        json={"name": "Master Updated"},
        headers={"Authorization": f"Bearer {master_token}"},
    )
    assert response.status_code == 200


def test_delete_club(client, db):
    user, token = make_user(db)
    create_resp = client.post(
        "/clubs", json={"name": "To Delete"}, headers={"Authorization": f"Bearer {token}"}
    )
    club_id = create_resp.json()["id"]

    response = client.delete(f"/clubs/{club_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 204

    get_resp = client.get(f"/clubs/{club_id}", headers={"Authorization": f"Bearer {token}"})
    assert get_resp.status_code == 404
