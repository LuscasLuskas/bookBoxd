"""reviews, review likes, club forum

Revision ID: 007
Revises: 006
Create Date: 2026-05-24

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "007"
down_revision: Union[str, None] = "006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- Reviews (rating + optional text; replaces user_books.rating) ---
    op.create_table(
        "reviews",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "user_id", sa.String(36),
            sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False,
        ),
        sa.Column(
            "book_id", sa.String(36),
            sa.ForeignKey("books.id", ondelete="CASCADE"), nullable=False,
        ),
        sa.Column("rating", sa.Float(), nullable=False),
        sa.Column("body", sa.Text(), nullable=True),
        sa.Column("is_public", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("user_id", "book_id", name="uq_review_user_book"),
    )
    op.create_index("ix_reviews_user_id", "reviews", ["user_id"])
    op.create_index("ix_reviews_book_id", "reviews", ["book_id"])

    # Backfill: every existing user_books.rating becomes a public, text-less review.
    op.execute(
        """
        INSERT INTO reviews (id, user_id, book_id, rating, body, is_public, created_at, updated_at)
        SELECT
            gen_random_uuid()::text,
            user_id,
            book_id,
            rating,
            NULL,
            TRUE,
            COALESCE(created_at, NOW()),
            COALESCE(updated_at, NOW())
        FROM user_books
        WHERE rating IS NOT NULL
        """
    )
    op.drop_column("user_books", "rating")

    # --- Review likes ---
    op.create_table(
        "review_likes",
        sa.Column(
            "review_id", sa.String(36),
            sa.ForeignKey("reviews.id", ondelete="CASCADE"), primary_key=True,
        ),
        sa.Column(
            "user_id", sa.String(36),
            sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    # --- Forum threads + posts ---
    op.create_table(
        "forum_threads",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "club_id", sa.String(36),
            sa.ForeignKey("book_clubs.id", ondelete="CASCADE"), nullable=False,
        ),
        sa.Column(
            "book_id", sa.String(36),
            sa.ForeignKey("books.id", ondelete="SET NULL"), nullable=True,
        ),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("is_pinned", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("auto_created", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column(
            "created_by", sa.String(36),
            sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_forum_threads_club_id", "forum_threads", ["club_id"])

    op.create_table(
        "forum_posts",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "thread_id", sa.String(36),
            sa.ForeignKey("forum_threads.id", ondelete="CASCADE"), nullable=False,
        ),
        sa.Column(
            "user_id", sa.String(36),
            sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True,
        ),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_forum_posts_thread_id", "forum_posts", ["thread_id"])


def downgrade() -> None:
    op.drop_table("forum_posts")
    op.drop_table("forum_threads")
    op.drop_table("review_likes")
    op.add_column("user_books", sa.Column("rating", sa.Float(), nullable=True))
    op.execute(
        """
        UPDATE user_books ub
        SET rating = r.rating
        FROM reviews r
        WHERE r.user_id = ub.user_id AND r.book_id = ub.book_id
        """
    )
    op.drop_table("reviews")
