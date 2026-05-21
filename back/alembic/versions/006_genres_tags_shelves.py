"""genres, tags and shelves

Revision ID: 006
Revises: 005
Create Date: 2026-05-21

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "006"
down_revision: Union[str, None] = "005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- Genres (book-level taxonomy, auto-imported from Open Library) ---
    op.create_table(
        "genres",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("name", name="uq_genre_name"),
    )
    op.create_table(
        "book_genres",
        sa.Column(
            "book_id", sa.String(36),
            sa.ForeignKey("books.id", ondelete="CASCADE"), primary_key=True,
        ),
        sa.Column(
            "genre_id", sa.String(36),
            sa.ForeignKey("genres.id", ondelete="CASCADE"), primary_key=True,
        ),
    )
    op.create_index("ix_book_genres_genre_id", "book_genres", ["genre_id"])

    # --- Tags (book-level, community/shared) ---
    op.create_table(
        "tags",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("name", name="uq_tag_name"),
    )
    op.create_table(
        "book_tags",
        sa.Column(
            "book_id", sa.String(36),
            sa.ForeignKey("books.id", ondelete="CASCADE"), primary_key=True,
        ),
        sa.Column(
            "tag_id", sa.String(36),
            sa.ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True,
        ),
        sa.Column(
            "added_by", sa.String(36),
            sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_book_tags_tag_id", "book_tags", ["tag_id"])

    # --- Shelves (user-owned custom collections) ---
    op.create_table(
        "shelves",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "user_id", sa.String(36),
            sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False,
        ),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("user_id", "name", name="uq_shelf_user_name"),
    )
    op.create_index("ix_shelves_user_id", "shelves", ["user_id"])
    op.create_table(
        "shelf_books",
        sa.Column(
            "shelf_id", sa.String(36),
            sa.ForeignKey("shelves.id", ondelete="CASCADE"), primary_key=True,
        ),
        sa.Column(
            "book_id", sa.String(36),
            sa.ForeignKey("books.id", ondelete="CASCADE"), primary_key=True,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_shelf_books_book_id", "shelf_books", ["book_id"])


def downgrade() -> None:
    op.drop_table("shelf_books")
    op.drop_table("shelves")
    op.drop_table("book_tags")
    op.drop_table("tags")
    op.drop_table("book_genres")
    op.drop_table("genres")
