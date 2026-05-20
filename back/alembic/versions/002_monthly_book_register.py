"""monthly book and reading register

Revision ID: 002
Revises: 001
Create Date: 2026-05-20

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "club_monthly_books",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "club_id",
            sa.String(36),
            sa.ForeignKey("book_clubs.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "book_id",
            sa.String(36),
            sa.ForeignKey("books.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "set_by",
            sa.String(36),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "start_date",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("end_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "is_active",
            sa.Boolean,
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index(
        "ix_club_monthly_books_club_id", "club_monthly_books", ["club_id"]
    )
    op.create_index(
        "ix_club_monthly_books_is_active", "club_monthly_books", ["is_active"]
    )

    op.create_table(
        "reading_registers",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "monthly_book_id",
            sa.String(36),
            sa.ForeignKey("club_monthly_books.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.String(36),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "unit",
            sa.Enum("PAGE", "CHAPTER", name="readingunit"),
            nullable=False,
            server_default="PAGE",
        ),
        sa.Column(
            "goal_frequency",
            sa.Enum("DAILY", "WEEKLY", name="goalfrequency"),
            nullable=False,
            server_default="DAILY",
        ),
        sa.Column("total_amount", sa.Integer, nullable=True),
        sa.Column(
            "current_position",
            sa.Integer,
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.UniqueConstraint(
            "monthly_book_id", "user_id", name="uq_reading_register_book_user"
        ),
    )
    op.create_index(
        "ix_reading_registers_monthly_book_id",
        "reading_registers",
        ["monthly_book_id"],
    )
    op.create_index(
        "ix_reading_registers_user_id", "reading_registers", ["user_id"]
    )


def downgrade() -> None:
    op.drop_table("reading_registers")
    op.drop_table("club_monthly_books")
    op.execute("DROP TYPE IF EXISTS readingunit")
    op.execute("DROP TYPE IF EXISTS goalfrequency")
