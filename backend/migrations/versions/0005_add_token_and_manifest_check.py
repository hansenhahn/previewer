"""add token and manifest check

Revision ID: 0005
Revises: 0004
Create Date: 2026-09-13
"""
from alembic import op
import sqlalchemy as sa

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "user_identities",
        sa.Column("access_token", sa.String(length=512), nullable=True),
    )
    op.add_column(
        "user_repositories",
        sa.Column("manifest_ok", sa.Boolean(), nullable=True),
    )
    op.add_column(
        "user_repositories",
        sa.Column("manifest_error", sa.String(length=255), nullable=True),
    )
    op.add_column(
        "user_repositories",
        sa.Column("checked_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("user_repositories", "checked_at")
    op.drop_column("user_repositories", "manifest_error")
    op.drop_column("user_repositories", "manifest_ok")
    op.drop_column("user_identities", "access_token")
