"""book open library fields

Revision ID: 003
Revises: 002
Create Date: 2026-05-20

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("books", sa.Column("cover_url", sa.String(500), nullable=True))
    op.add_column("books", sa.Column("external_id", sa.String(100), nullable=True))
    op.add_column("books", sa.Column("published_year", sa.Integer, nullable=True))
    op.add_column("books", sa.Column("isbn", sa.String(20), nullable=True))
    op.create_index("ix_books_external_id", "books", ["external_id"])


def downgrade() -> None:
    op.drop_index("ix_books_external_id", table_name="books")
    op.drop_column("books", "isbn")
    op.drop_column("books", "published_year")
    op.drop_column("books", "external_id")
    op.drop_column("books", "cover_url")
