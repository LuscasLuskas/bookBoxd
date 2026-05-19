"""Tests for UserBook personal library (T10)."""
from tests.conftest import make_user


def create_book(client, token):
    resp = client.post(
        "/books",
        json={"title": "My Book", "author": "Author"},
        headers={"Authorization": f"Bearer {token}"},
    )
    return resp.json()["id"]


def test_add_to_library(client, db):
    user, token = make_user(db)
    book_id = create_book(client, token)

    response = client.post(
        "/me/books",
        json={"book_id": book_id, "status": "READING"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    assert response.json()["status"] == "READING"


def test_add_duplicate_returns_409(client, db):
    user, token = make_user(db)
    book_id = create_book(client, token)

    client.post("/me/books", json={"book_id": book_id}, headers={"Authorization": f"Bearer {token}"})
    response = client.post("/me/books", json={"book_id": book_id}, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 409


def test_list_library(client, db):
    user, token = make_user(db)
    book_id = create_book(client, token)
    client.post("/me/books", json={"book_id": book_id}, headers={"Authorization": f"Bearer {token}"})

    response = client.get("/me/books", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["total"] == 1


def test_update_book_status(client, db):
    user, token = make_user(db)
    book_id = create_book(client, token)
    client.post("/me/books", json={"book_id": book_id, "status": "WISHLIST"}, headers={"Authorization": f"Bearer {token}"})

    response = client.patch(
        f"/me/books/{book_id}",
        json={"status": "COMPLETED"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "COMPLETED"


def test_remove_from_library(client, db):
    user, token = make_user(db)
    book_id = create_book(client, token)
    client.post("/me/books", json={"book_id": book_id}, headers={"Authorization": f"Bearer {token}"})

    response = client.delete(f"/me/books/{book_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 204

    list_resp = client.get("/me/books", headers={"Authorization": f"Bearer {token}"})
    assert list_resp.json()["total"] == 0


def test_filter_by_status(client, db):
    user, token = make_user(db)
    book_id1 = create_book(client, token)
    book_id2 = create_book(client, token)
    client.post("/me/books", json={"book_id": book_id1, "status": "READING"}, headers={"Authorization": f"Bearer {token}"})
    client.post("/me/books", json={"book_id": book_id2, "status": "COMPLETED"}, headers={"Authorization": f"Bearer {token}"})

    response = client.get("/me/books?status=READING", headers={"Authorization": f"Bearer {token}"})
    assert response.json()["total"] == 1
