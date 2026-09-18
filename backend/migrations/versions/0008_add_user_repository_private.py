"""add user repository private flag

Revision ID: 0008
Revises: 0007
Create Date: 2026-09-16
"""
from alembic import op
import sqlalchemy as sa

revision = "0008"
down_revision = "0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "user_repositories",
        sa.Column("private", sa.Boolean(), nullable=False, server_default=sa.false()),
    )


def downgrade() -> None:
    op.drop_column("user_repositories", "private")
