"""Tests for monthly books and personal reading registers."""
from app.models.user import Role
from tests.conftest import make_user


def auth(token):
    return {"Authorization": f"Bearer {token}"}


def create_club(client, token, name="Club"):
    resp = client.post("/clubs", json={"name": name}, headers=auth(token))
    return resp.json()["id"]


def create_book(client, token, title="Test Book"):
    resp = client.post(
        "/books", json={"title": title, "author": "Author"}, headers=auth(token)
    )
    return resp.json()["id"]


def add_active_member(client, db, club_id, owner_token, name="Member"):
    """Cria um usuário, faz pedido de entrada e o aprova como owner."""
    member, token = make_user(db, name=name)
    client.post(f"/clubs/{club_id}/join", headers=auth(token))
    client.post(
        f"/clubs/{club_id}/members/{member.id}/approve", headers=auth(owner_token)
    )
    return member, token


def set_monthly_book(client, token, club_id, book_id):
    return client.post(
        f"/clubs/{club_id}/monthly-books",
        json={"book_id": book_id},
        headers=auth(token),
    )


# ---- definir o livro do mês ----


def test_set_monthly_book(client, db):
    owner, token = make_user(db)
    club_id = create_club(client, token)
    book_id = create_book(client, token)

    resp = set_monthly_book(client, token, club_id, book_id)
    assert resp.status_code == 201
    body = resp.json()
    assert body["book_id"] == book_id
    assert body["is_active"] is True
    assert body["cycle_days"] == 30
    assert body["member_count"] == 1  # o owner já é membro ativo


def test_set_monthly_book_creates_register_for_each_active_member(client, db):
    owner, owner_token = make_user(db, name="Owner")
    club_id = create_club(client, owner_token)
    book_id = create_book(client, owner_token)
    _, member_token = add_active_member(client, db, club_id, owner_token)

    resp = set_monthly_book(client, owner_token, club_id, book_id)
    assert resp.status_code == 201
    assert resp.json()["member_count"] == 2

    mb_id = resp.json()["id"]
    r1 = client.get(
        f"/clubs/{club_id}/monthly-books/{mb_id}/register", headers=auth(owner_token)
    )
    r2 = client.get(
        f"/clubs/{club_id}/monthly-books/{mb_id}/register",
        headers=auth(member_token),
    )
    assert r1.status_code == 200
    assert r2.status_code == 200


def test_non_owner_cannot_set_monthly_book(client, db):
    owner, owner_token = make_user(db, name="Owner")
    _, other_token = make_user(db, name="Other")
    club_id = create_club(client, owner_token)
    book_id = create_book(client, owner_token)

    resp = set_monthly_book(client, other_token, club_id, book_id)
    assert resp.status_code == 403


def test_master_can_set_monthly_book(client, db):
    owner, owner_token = make_user(db, name="Owner")
    _, master_token = make_user(db, role=Role.MASTER, name="Master")
    club_id = create_club(client, owner_token)
    book_id = create_book(client, owner_token)

    resp = set_monthly_book(client, master_token, club_id, book_id)
    assert resp.status_code == 201


def test_set_monthly_book_nonexistent_book_404(client, db):
    owner, token = make_user(db)
    club_id = create_club(client, token)

    resp = set_monthly_book(client, token, club_id, "does-not-exist")
    assert resp.status_code == 404


def test_set_same_book_twice_returns_409(client, db):
    owner, token = make_user(db)
    club_id = create_club(client, token)
    book_id = create_book(client, token)

    set_monthly_book(client, token, club_id, book_id)
    resp = set_monthly_book(client, token, club_id, book_id)
    assert resp.status_code == 409


def test_club_can_have_multiple_active_monthly_books(client, db):
    owner, token = make_user(db)
    club_id = create_club(client, token)
    book1 = create_book(client, token, title="Book One")
    book2 = create_book(client, token, title="Book Two")

    assert set_monthly_book(client, token, club_id, book1).status_code == 201
    assert set_monthly_book(client, token, club_id, book2).status_code == 201

    resp = client.get(f"/clubs/{club_id}/monthly-books", headers=auth(token))
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 2
    assert all(item["is_active"] for item in body["items"])


# ---- visualizar ----


def test_get_monthly_book(client, db):
    owner, token = make_user(db)
    club_id = create_club(client, token)
    book_id = create_book(client, token)
    mb_id = set_monthly_book(client, token, club_id, book_id).json()["id"]

    resp = client.get(
        f"/clubs/{club_id}/monthly-books/{mb_id}", headers=auth(token)
    )
    assert resp.status_code == 200
    assert resp.json()["id"] == mb_id


def test_get_monthly_book_404(client, db):
    owner, token = make_user(db)
    club_id = create_club(client, token)

    resp = client.get(
        f"/clubs/{club_id}/monthly-books/missing", headers=auth(token)
    )
    assert resp.status_code == 404


def test_non_member_cannot_view_monthly_books(client, db):
    owner, owner_token = make_user(db, name="Owner")
    _, outsider_token = make_user(db, name="Outsider")
    club_id = create_club(client, owner_token)
    book_id = create_book(client, owner_token)
    set_monthly_book(client, owner_token, club_id, book_id)

    resp = client.get(
        f"/clubs/{club_id}/monthly-books", headers=auth(outsider_token)
    )
    assert resp.status_code == 403


# ---- registro de leitura ----


def test_configure_register_computes_goal(client, db):
    owner, token = make_user(db)
    club_id = create_club(client, token)
    book_id = create_book(client, token)
    mb_id = set_monthly_book(client, token, club_id, book_id).json()["id"]

    resp = client.patch(
        f"/clubs/{club_id}/monthly-books/{mb_id}/register",
        json={"unit": "PAGE", "total_amount": 300},
        headers=auth(token),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["is_configured"] is True
    assert body["daily_goal"] == 10  # 300 páginas / 30 dias
    assert body["current_goal"] == 10


def test_register_goal_frequency_switch(client, db):
    owner, token = make_user(db)
    club_id = create_club(client, token)
    book_id = create_book(client, token)
    mb_id = set_monthly_book(client, token, club_id, book_id).json()["id"]

    client.patch(
        f"/clubs/{club_id}/monthly-books/{mb_id}/register",
        json={"total_amount": 300},
        headers=auth(token),
    )
    resp = client.patch(
        f"/clubs/{club_id}/monthly-books/{mb_id}/register",
        json={"goal_frequency": "WEEKLY"},
        headers=auth(token),
    )
    body = resp.json()
    assert body["goal_frequency"] == "WEEKLY"
    assert body["current_goal"] == body["weekly_goal"]


def test_register_track_by_chapter(client, db):
    owner, token = make_user(db)
    club_id = create_club(client, token)
    book_id = create_book(client, token)
    mb_id = set_monthly_book(client, token, club_id, book_id).json()["id"]

    resp = client.patch(
        f"/clubs/{club_id}/monthly-books/{mb_id}/register",
        json={"unit": "CHAPTER", "total_amount": 40, "current_position": 8},
        headers=auth(token),
    )
    body = resp.json()
    assert body["unit"] == "CHAPTER"
    assert body["progress_percent"] == 20.0
    assert body["amount_remaining"] == 32


def test_register_position_cannot_exceed_total(client, db):
    owner, token = make_user(db)
    club_id = create_club(client, token)
    book_id = create_book(client, token)
    mb_id = set_monthly_book(client, token, club_id, book_id).json()["id"]

    client.patch(
        f"/clubs/{club_id}/monthly-books/{mb_id}/register",
        json={"total_amount": 100},
        headers=auth(token),
    )
    resp = client.patch(
        f"/clubs/{club_id}/monthly-books/{mb_id}/register",
        json={"current_position": 500},
        headers=auth(token),
    )
    assert resp.status_code == 400


def test_register_completion(client, db):
    owner, token = make_user(db)
    club_id = create_club(client, token)
    book_id = create_book(client, token)
    mb_id = set_monthly_book(client, token, club_id, book_id).json()["id"]

    resp = client.patch(
        f"/clubs/{club_id}/monthly-books/{mb_id}/register",
        json={"total_amount": 100, "current_position": 100},
        headers=auth(token),
    )
    body = resp.json()
    assert body["is_completed"] is True
    assert body["progress_percent"] == 100.0
    assert body["amount_remaining"] == 0


def test_non_member_cannot_access_register(client, db):
    owner, owner_token = make_user(db, name="Owner")
    _, outsider_token = make_user(db, name="Outsider")
    club_id = create_club(client, owner_token)
    book_id = create_book(client, owner_token)
    mb_id = set_monthly_book(client, owner_token, club_id, book_id).json()["id"]

    resp = client.get(
        f"/clubs/{club_id}/monthly-books/{mb_id}/register",
        headers=auth(outsider_token),
    )
    assert resp.status_code == 403


def test_late_joiner_gets_register_lazily(client, db):
    owner, owner_token = make_user(db)
    club_id = create_club(client, owner_token)
    book_id = create_book(client, owner_token)
    mb_id = set_monthly_book(client, owner_token, club_id, book_id).json()["id"]

    # o membro entra DEPOIS de o livro do mês ter sido definido
    member, member_token = add_active_member(client, db, club_id, owner_token)
    resp = client.get(
        f"/clubs/{club_id}/monthly-books/{mb_id}/register",
        headers=auth(member_token),
    )
    assert resp.status_code == 200
    assert resp.json()["user_id"] == member.id


# ---- placar ----


def test_leaderboard_sorted_by_progress(client, db):
    owner, owner_token = make_user(db, name="Owner")
    club_id = create_club(client, owner_token)
    book_id = create_book(client, owner_token)
    _, member_token = add_active_member(client, db, club_id, owner_token)
    mb_id = set_monthly_book(client, owner_token, club_id, book_id).json()["id"]

    client.patch(
        f"/clubs/{club_id}/monthly-books/{mb_id}/register",
        json={"total_amount": 100, "current_position": 10},
        headers=auth(owner_token),
    )
    client.patch(
        f"/clubs/{club_id}/monthly-books/{mb_id}/register",
        json={"total_amount": 100, "current_position": 80},
        headers=auth(member_token),
    )

    resp = client.get(
        f"/clubs/{club_id}/monthly-books/{mb_id}/registers",
        headers=auth(owner_token),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 2
    assert (
        body["items"][0]["progress_percent"]
        >= body["items"][1]["progress_percent"]
    )
    assert body["items"][0]["current_position"] == 80


# ---- encerrar ----


def test_clear_monthly_book(client, db):
    owner, token = make_user(db)
    club_id = create_club(client, token)
    book_id = create_book(client, token)
    mb_id = set_monthly_book(client, token, club_id, book_id).json()["id"]

    resp = client.delete(
        f"/clubs/{club_id}/monthly-books/{mb_id}", headers=auth(token)
    )
    assert resp.status_code == 204

    got = client.get(
        f"/clubs/{club_id}/monthly-books/{mb_id}", headers=auth(token)
    )
    assert got.json()["is_active"] is False


def test_clear_already_ended_returns_400(client, db):
    owner, token = make_user(db)
    club_id = create_club(client, token)
    book_id = create_book(client, token)
    mb_id = set_monthly_book(client, token, club_id, book_id).json()["id"]

    client.delete(f"/clubs/{club_id}/monthly-books/{mb_id}", headers=auth(token))
    resp = client.delete(
        f"/clubs/{club_id}/monthly-books/{mb_id}", headers=auth(token)
    )
    assert resp.status_code == 400


def test_non_owner_cannot_clear_monthly_book(client, db):
    owner, owner_token = make_user(db, name="Owner")
    club_id = create_club(client, owner_token)
    book_id = create_book(client, owner_token)
    mb_id = set_monthly_book(client, owner_token, club_id, book_id).json()["id"]
    _, member_token = add_active_member(client, db, club_id, owner_token)

    resp = client.delete(
        f"/clubs/{club_id}/monthly-books/{mb_id}", headers=auth(member_token)
    )
    assert resp.status_code == 403
