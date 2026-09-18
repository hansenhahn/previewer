from infra.models import Change, Project, User, UserIdentity, UserRepository


def test_project_columns():
    columns = set(Project.__table__.columns.keys())
    assert {
        "id",
        "owner_id",
        "name",
        "encoding",
        "upstream",
        "base_branch",
        "created_at",
        "updated_at",
    } <= columns


def test_project_unique_constraint_by_owner_and_name():
    names = {constraint.name for constraint in Project.__table__.constraints}
    assert "uq_projects_owner_name" in names


def test_user_identity_columns_and_unique_constraint():
    columns = set(UserIdentity.__table__.columns.keys())
    assert {"id", "user_id", "provider", "external_id", "login", "email", "avatar_url"} <= columns
    names = {constraint.name for constraint in UserIdentity.__table__.constraints}
    assert "uq_user_identities_provider_external" in names
    assert "users" == User.__tablename__


def test_user_repository_columns_and_unique_constraint():
    columns = set(UserRepository.__table__.columns.keys())
    assert {
        "id",
        "user_id",
        "provider",
        "full_name",
        "default_branch",
        "fork",
        "private",
        "manifest_ok",
        "manifest_error",
        "checked_at",
    } <= columns
    names = {constraint.name for constraint in UserRepository.__table__.constraints}
    assert "uq_user_repositories_user_provider_name" in names


def test_change_columns_and_unique_constraint():
    columns = set(Change.__table__.columns.keys())
    assert {
        "id",
        "project_id",
        "user_id",
        "branch",
        "title",
        "base_commit",
        "pr_number",
        "status",
        "created_at",
        "updated_at",
    } <= columns
    names = {constraint.name for constraint in Change.__table__.constraints}
    assert "uq_changes_project_user_branch" in names
