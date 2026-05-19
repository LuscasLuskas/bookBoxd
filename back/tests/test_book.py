"""Tests for Book CRUD (T06)."""
from tests.conftest import make_user


def test_create_book(client, db):
    user, token = make_user(db)
    response = client.post(
        "/books",
        json={"title": "Dom Quixote", "author": "Cervantes", "synopsis": "Um clássico"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Dom Quixote"
    assert data["created_by"] == user.id
    assert data["created_by_name_snapshot"] == user.name


def test_list_books(client, db):
    user, token = make_user(db)
    client.post(
        "/books",
        json={"title": "Livro A", "author": "Autor A"},
        headers={"Authorization": f"Bearer {token}"},
    )
    client.post(
        "/books",
        json={"title": "Livro B", "author": "Autor B"},
        headers={"Authorization": f"Bearer {token}"},
    )
    response = client.get("/books", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["total"] == 2


def test_list_books_filter_title(client, db):
    user, token = make_user(db)
    client.post("/books", json={"title": "Python Deep Dive", "author": "Author"}, headers={"Authorization": f"Bearer {token}"})
    client.post("/books", json={"title": "Java Basics", "author": "Author"}, headers={"Authorization": f"Bearer {token}"})

    response = client.get("/books?title=python", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["total"] == 1


def test_get_book_by_id(client, db):
    user, token = make_user(db)
    create_resp = client.post(
        "/books",
        json={"title": "Unique Book", "author": "Author"},
        headers={"Authorization": f"Bearer {token}"},
    )
    book_id = create_resp.json()["id"]

    response = client.get(f"/books/{book_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["id"] == book_id


def test_get_book_not_found(client, db):
    user, token = make_user(db)
    response = client.get("/books/nonexistent-id", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404
