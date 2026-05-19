"""Tests for ClubBook (T09)."""
from app.models.user import Role
from tests.conftest import make_user


def create_club(client, token):
    resp = client.post("/clubs", json={"name": "Club"}, headers={"Authorization": f"Bearer {token}"})
    return resp.json()["id"]


def create_book(client, token):
    resp = client.post(
        "/books",
        json={"title": "Test Book", "author": "Author"},
        headers={"Authorization": f"Bearer {token}"},
    )
    return resp.json()["id"]


def test_add_book_to_club(client, db):
    owner, token = make_user(db)
    club_id = create_club(client, token)
    book_id = create_book(client, token)

    response = client.post(
        f"/clubs/{club_id}/books",
        json={"book_id": book_id},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    assert response.json()["book_id"] == book_id


def test_add_book_duplicate_returns_409(client, db):
    owner, token = make_user(db)
    club_id = create_club(client, token)
    book_id = create_book(client, token)

    client.post(f"/clubs/{club_id}/books", json={"book_id": book_id}, headers={"Authorization": f"Bearer {token}"})
    response = client.post(f"/clubs/{club_id}/books", json={"book_id": book_id}, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 409


def test_non_owner_cannot_add_book(client, db):
    owner, owner_token = make_user(db, name="Owner")
    other, other_token = make_user(db, name="Other")
    club_id = create_club(client, owner_token)
    book_id = create_book(client, owner_token)

    response = client.post(
        f"/clubs/{club_id}/books",
        json={"book_id": book_id},
        headers={"Authorization": f"Bearer {other_token}"},
    )
    assert response.status_code == 403


def test_list_club_books(client, db):
    owner, token = make_user(db)
    club_id = create_club(client, token)
    book_id = create_book(client, token)
    client.post(f"/clubs/{club_id}/books", json={"book_id": book_id}, headers={"Authorization": f"Bearer {token}"})

    response = client.get(f"/clubs/{club_id}/books", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["total"] == 1


def test_remove_book_from_club(client, db):
    owner, token = make_user(db)
    club_id = create_club(client, token)
    book_id = create_book(client, token)
    client.post(f"/clubs/{club_id}/books", json={"book_id": book_id}, headers={"Authorization": f"Bearer {token}"})

    response = client.delete(f"/clubs/{club_id}/books/{book_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 204
