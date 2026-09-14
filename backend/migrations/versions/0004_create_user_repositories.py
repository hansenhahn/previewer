"""create user repositories

Revision ID: 0004
Revises: 0003
Create Date: 2026-09-13
"""
from alembic import op
import sqlalchemy as sa

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user_repositories",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("provider", sa.String(length=64), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("default_branch", sa.String(length=255), nullable=False),
        sa.Column("fork", sa.Boolean(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id",
            "provider",
            "full_name",
            name="uq_user_repositories_user_provider_name",
        ),
    )
    op.create_index("ix_user_repositories_user_id", "user_repositories", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_user_repositories_user_id", table_name="user_repositories")
    op.drop_table("user_repositories")
