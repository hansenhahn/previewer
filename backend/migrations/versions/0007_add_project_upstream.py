"""add project upstream and base branch

Revision ID: 0007
Revises: 0006
Create Date: 2026-09-15
"""
from alembic import op
import sqlalchemy as sa

revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "projects", sa.Column("upstream", sa.String(length=255), nullable=True)
    )
    op.add_column(
        "projects", sa.Column("base_branch", sa.String(length=255), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("projects", "base_branch")
    op.drop_column("projects", "upstream")
