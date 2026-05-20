"""user profile fields

Revision ID: 004
Revises: 003
Create Date: 2026-05-20

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("avatar_url", sa.String(500), nullable=True))
    op.add_column("users", sa.Column("bio", sa.Text, nullable=True))
    op.add_column("users", sa.Column("favorite_book_id", sa.String(36), nullable=True))
    op.create_foreign_key(
        "fk_users_favorite_book",
        "users",
        "books",
        ["favorite_book_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_users_favorite_book", "users", type_="foreignkey")
    op.drop_column("users", "favorite_book_id")
    op.drop_column("users", "bio")
    op.drop_column("users", "avatar_url")
