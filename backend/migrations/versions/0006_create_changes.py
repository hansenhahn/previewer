"""create changes

Revision ID: 0006
Revises: 0005
Create Date: 2026-09-15
"""
from alembic import op
import sqlalchemy as sa

revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "changes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("branch", sa.String(length=255), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("base_commit", sa.String(length=64), nullable=True),
        sa.Column("pr_number", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "project_id",
            "user_id",
            "branch",
            name="uq_changes_project_user_branch",
        ),
    )
    op.create_index("ix_changes_project_id", "changes", ["project_id"])
    op.create_index("ix_changes_user_id", "changes", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_changes_user_id", table_name="changes")
    op.drop_index("ix_changes_project_id", table_name="changes")
    op.drop_table("changes")
