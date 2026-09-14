"""add avatar to user identities

Revision ID: 0003
Revises: 0002
Create Date: 2026-09-13
"""
from alembic import op
import sqlalchemy as sa

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "user_identities",
        sa.Column("avatar_url", sa.String(length=512), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("user_identities", "avatar_url")
