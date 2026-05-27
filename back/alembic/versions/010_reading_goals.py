"""reading goals and daily logs

Revision ID: 010
Revises: 009
Create Date: 2026-05-26

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "010"
down_revision: Union[str, None] = "009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- Personal daily reading goal (one per user) ---
    op.create_table(
        "reading_goals",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "user_id", sa.String(36),
            sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False,
        ),
        sa.Column("pages_per_day", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("user_id", name="uq_reading_goal_user"),
    )
    op.create_index("ix_reading_goals_user_id", "reading_goals", ["user_id"])

    # --- Per-day reading log (one row per user per calendar day) ---
    op.create_table(
        "daily_reading_logs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "user_id", sa.String(36),
            sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False,
        ),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("pages_read", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("goal_target", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("user_id", "date", name="uq_daily_log_user_date"),
    )
    op.create_index("ix_daily_reading_logs_user_id", "daily_reading_logs", ["user_id"])
    op.create_index("ix_daily_reading_logs_date", "daily_reading_logs", ["date"])


def downgrade() -> None:
    op.drop_table("daily_reading_logs")
    op.drop_table("reading_goals")
